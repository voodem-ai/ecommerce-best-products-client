"""MCP Client Agent – connects to the MCP server, registers tools with Gemini,
and runs an agentic tool-calling loop."""

import asyncio
import json
from typing import Any

import structlog
from google import genai
from google.genai import types
from mcp.client.sse import sse_client
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
    # Prioritize AI Studio (API Key) over Vertex AI (GCP)
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
        gemini = genai.Client(api_key=settings.GEMINI_API_KEY)
    elif hasattr(settings, "GOOGLE_CLOUD_PROJECT") and settings.GOOGLE_CLOUD_PROJECT:
        location = getattr(settings, "GOOGLE_CLOUD_LOCATION", None)
        gemini = genai.Client(
            vertexai=True, project=settings.GOOGLE_CLOUD_PROJECT, location=location
        )
    else:
        # Fallback to auto-discovery
        gemini = genai.Client()

    async with sse_client(settings.MCP_SERVER_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
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

                # Execute each tool call on the MCP server IN PARALLEL
                tool_response_parts: list[types.Part] = []
                
                async def execute_tool(fc):
                    log.info("calling_tool", name=fc.name, args=fc.args)
                    try:
                        result = await session.call_tool(fc.name, arguments=fc.args or {})
                        return types.Part(
                            function_response=types.FunctionResponse(
                                name=fc.name,
                                response={"result": _parse_content(result.content)},
                            )
                        )
                    except Exception as e:
                        log.error("tool_execution_failed", name=fc.name, error=str(e))
                        return types.Part(
                            function_response=types.FunctionResponse(
                                name=fc.name,
                                response={"error": f"Failed to execute tool: {str(e)}"},
                            )
                        )

                # Gather all tool executions concurrently
                tool_response_parts = await asyncio.gather(
                    *(execute_tool(fc) for fc in response.function_calls)
                )

                contents.append(types.Content(role="user", parts=list(tool_response_parts)))

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
