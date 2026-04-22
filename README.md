# E-Commerce Best Products – MCP Client

An MCP Client that orchestrates **Google Gemini AI** with MCP Server tools to deliver intelligent product recommendations from Amazon, Flipkart, and Myntra — displayed as a ranked HTML table in the React UI.

---

## Architecture

### High-Level System Flow
```
React UI (port 3000)
     │  POST /recommend {"prompt": "best running shoes under ₹3000"}
     ▼
MCP Client (port 8001)  ──SSE──▶  MCP Server (port 8000)
     │                                     │
     │  Gemini Agentic Loop                │  Gemini Search Grounding
     │  (google-genai SDK)                 │  (Amazon + Flipkart + Myntra)
     └─────────────────────────────────────┘
```

### Low-Level Request Flow (Client)

```
POST /recommend  {"prompt": "best wireless earbuds under ₹2000"}
         │
         ▼
  main.py :: /recommend endpoint
         │
         ├──► cache.py :: cache_get(SHA256(prompt))
         │         └─► Redis HIT → return cached response immediately
         │
         ▼ (cache miss)
  agent.py :: run_agent(user_prompt)
         │
         ├── Step 1: Initialise Gemini client
         │     GEMINI_API_KEY set? → genai.Client(api_key=...)
         │     No API key?         → genai.Client(vertexai=True, project=...)
         │
         ├── Step 2: Connect to MCP Server via SSE
         │     sse_client("http://localhost:8000/mcp/sse")
         │       │  Opens SSE stream → receives session_id endpoint
         │       └─► Creates read_stream + write_stream pair
         │     ClientSession(read_stream, write_stream)
         │       └─► session.initialize()  [MCP handshake]
         │
         ├── Step 3: Discover available tools
         │     session.list_tools()
         │       └─► ["search_amazon", "search_flipkart", "search_myntra"]
         │     Map each tool → Gemini FunctionDeclaration
         │
         ├── Step 4: Agentic Loop (max 5 rounds)
         │     │
         │     ├── gemini.models.generate_content(
         │     │     model="gemini-2.5-flash",
         │     │     contents=[user_prompt, ...tool_results],
         │     │     tools=[search_amazon, search_flipkart, search_myntra],
         │     │     system_instruction="...return top 3 as HTML table..."
         │     │   )
         │     │
         │     ├── No function_calls in response?
         │     │       └─► DONE → return response.text (final answer)
         │     │
         │     └── Has function_calls? → Execute ALL in PARALLEL:
         │           asyncio.gather(
         │             execute_tool(search_amazon,   args),  ─┐
         │             execute_tool(search_flipkart, args),   ├─ concurrent
         │             execute_tool(search_myntra,   args),  ─┘
         │           )
         │           Each execute_tool():
         │             session.call_tool(name, arguments)
         │               └─► MCP JSON-RPC → Server scrapes → returns products
         │           Append all tool results → next generation round
         │
         ├── Step 5: Format response
         │     Gemini returns HTML table:
         │     <table class="styled-table">
         │       <thead><tr><th>Rank</th><th>Product</th>
         │                  <th>Price</th><th>Link</th><th>Reason</th></tr></thead>
         │       <tbody>
         │         <tr><td>1</td><td>Nike Revolution 8</td><td>₹4295</td>
         │             <td><a href="https://amazon.in/...">Link</a></td>
         │             <td>Highest rated (4.3★) with 1,500 reviews</td></tr>
         │         ...
         │       </tbody>
         │     </table>
         │
         ▼
  cache.py :: cache_set(SHA256(prompt), response, TTL=1800s)
         │
         ▼
  Return {"recommendation": "<html table>", "products": [], "cached": false}
         │
         ▼
React UI renders table with premium CSS glassmorphic styling
```

### Gemini Tool-Calling Protocol
```
Client ──generate_content──▶ Gemini
                              │  Gemini decides which tools to call
                              ▼
       ◀──function_calls────── [{"name":"search_amazon","args":{"query":"earbuds"}}]

Client ──call_tool──▶ MCP Server ──scrape──▶ Amazon/Flipkart/Myntra
       ◀─────────── products JSON ───────────

Client ──generate_content──▶ Gemini (with tool results)
                              │  Gemini synthesises final recommendation
                              ▼
       ◀──text response──────── "Here are the top 3..."
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Build Tool | Poetry |
| AI Model | Google Gemini 2.5 Flash (via `google-genai` SDK) |
| MCP | MCP Python SDK – `mcp.client.sse.sse_client` |
| MCP Transport | SSE (Server-Sent Events) |
| Web Framework | FastAPI + Uvicorn |
| Data Models | Pydantic v2 |
| Caching | Redis (prompt-level SHA-256 hashing, graceful fallback) |
| Logging | structlog (structured JSON) |
| Config | python-dotenv + environment variables |
| Container | Docker (multi-stage) |
| Deployment | Helm chart with internal ClusterIP Service |

---

## Quick Start

### 1. Clone & Configure
```bash
git clone https://github.com/voodem-ai/ecommerce-best-products-client.git
cd ecommerce-best-products-client
cp .env.example .env
# Edit .env — GEMINI_API_KEY is REQUIRED
```

### 2. Get a Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Paste it into `.env` as `GEMINI_API_KEY`

### 3. Install & Run
```bash
poetry install
poetry run uvicorn client.main:app --reload --port 8001
```

### 4. Docker
```bash
docker build -t mcp-client .
docker run -p 8001:8001 --env-file .env mcp-client
```

---

## Environment Variables (`.env`)

| Variable | Default | Required | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | – | **Yes** | Google Gemini API key from [AI Studio](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | No | Gemini model ID |
| `MCP_SERVER_URL` | `http://localhost:8000/mcp/sse` | No | MCP Server SSE endpoint |
| `REDIS_HOST` | `localhost` | No | Redis hostname |
| `REDIS_PORT` | `6379` | No | Redis port |
| `REDIS_TTL` | `1800` | No | Response cache TTL (seconds) |
| `CLIENT_HOST` | `0.0.0.0` | No | Bind address |
| `CLIENT_PORT` | `8001` | No | Bind port |
| `GOOGLE_APPLICATION_CREDENTIALS` | – | No | GCP service account JSON (Vertex AI fallback) |
| `GOOGLE_CLOUD_PROJECT` | – | No | GCP project (Vertex AI fallback only) |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | No | GCP region (Vertex AI fallback only) |

> **Important:** `GEMINI_API_KEY` takes priority. Vertex AI credentials are only used if no API key is set.

### Gemini Access Options

| Method | When to Use | Config |
|---|---|---|
| **AI Studio API Key** | Development, prototyping | Set `GEMINI_API_KEY` |
| **Vertex AI** | Production/enterprise (billing required) | Set `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT` |

---

## API

### `POST /recommend`
**Request:**
```json
{ "prompt": "I need the best wireless earbuds under ₹2000" }
```

**Response:**
```json
{
  "recommendation": "<table class='styled-table'>..top 3 products as HTML table..</table>",
  "products": [],
  "cached": false
}
```

### `GET /health`
```json
{ "status": "ok" }
```

---

## Project Structure

```
src/client/
├── __init__.py
├── main.py       # FastAPI entry point (/recommend, /health)
├── config.py     # .env + environment settings (API key priority logic)
├── cache.py      # SHA-256 prompt-level Redis cache
├── models.py     # Pydantic request/response models
└── agent.py      # Gemini agentic loop + parallel MCP tool execution
helm/
└── ecommerce-client/   # Helm chart deployment files
```

---

## Testing

```bash
poetry run pytest tests/ -v
```

## License
MIT
