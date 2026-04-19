"""MCP Client Agent – connects to the MCP server, registers tools with Gemini,
and runs an agentic tool-calling loop."""

import json
from typing import Any

import structlog
from google import genai
from google.genai import types
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

from client.config import settings

log = structlog.get_logger()


async def run_agent(user_prompt: str) -> str:
    """Execute the full MCP → Gemini agentic loop.

    1. Connect to the MCP server via Streamable HTTP.
    2. Discover available tools.
    3. Ask Gemini to answer the user prompt using those tools.
    4. Execute any tool calls on the server as the Gemini model calls them, 
       feed results back, and return the final answer.
    """
    # Support both Google AI Studio (API Key) and Vertex AI (GCP)
    if hasattr(settings, "GOOGLE_CLOUD_PROJECT") and settings.GOOGLE_CLOUD_PROJECT:
        location = getattr(settings, "GOOGLE_CLOUD_LOCATION", None)
        gemini = genai.Client(
            vertexai=True, project=settings.GOOGLE_CLOUD_PROJECT, location=location
        )
    elif settings.GEMINI_API_KEY:
        gemini = genai.Client(api_key=settings.GEMINI_API_KEY)
    else:
        # Fallback to auto-discovery
        gemini = genai.Client()

    async with streamablehttp_client(settings.MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # ---- Discover tools from MCP server --------------------------
            tools_result = await session.list_tools()

            gemini_tools = []
            for tool in tools_result.tools:
                gemini_tools.append(types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=tool.name,
                            description=tool.description or "",
                            parameters=tool.inputSchema,
                        )
                    ]
                ))

            log.info(
                "tools_discovered",
                count=len(gemini_tools),
                names=[t.name for t in tools_result.tools],
            )

            # ---- Build the initial prompt --------------------------------
            system_instruction = (
                "You are an expert shopping assistant. The user wants product "
                "recommendations. Use the available tools to search across "
                "Amazon, Flipkart, and Myntra. Always prioritise products that "
                "are: (1) top-rated, (2) lowest price, (3) most buyers. "
                "After gathering results, provide a clear, well-formatted "
                "comparison with your recommendation."
            )

            contents: list[types.Content] = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=user_prompt)],
                ),
            ]

            # ---- Agentic loop (max 5 rounds) ----------------------------
            for _round in range(5):
                response = gemini.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        tools=gemini_tools,
                        system_instruction=system_instruction,
                    ),
                )

                # If there are no function calls, we have a final answer
                if not response.function_calls:
                    return response.text or "No recommendation generated."

                # Append the model's response (with tool-call requests)
                contents.append(response.candidates[0].content)

                # Execute each tool call on the MCP server
                tool_response_parts: list[types.Part] = []
                for fc in response.function_calls:
                    log.info("calling_tool", name=fc.name, args=fc.args)
                    result = await session.call_tool(fc.name, arguments=fc.args or {})

                    # Build function-response part
                    tool_response_parts.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=fc.name,
                                response={"result": _parse_content(result.content)},
                            )
                        )
                    )

                contents.append(types.Content(role="user", parts=tool_response_parts))

            return "Max tool-calling rounds reached. Please try a simpler query."


def _parse_content(content: Any) -> Any:
    """Best-effort extract text from MCP tool result content blocks."""
    if isinstance(content, list):
        texts = []
        for block in content:
            if hasattr(block, "text"):
                texts.append(block.text)
        combined = " ".join(texts)
        try:
            return json.loads(combined)
        except (json.JSONDecodeError, TypeError):
            return combined
    return str(content)
