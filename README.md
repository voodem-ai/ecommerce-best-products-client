# E-Commerce Best Products – MCP Client

An MCP Client that orchestrates **Google Gemini AI** with MCP Server tools to deliver intelligent product recommendations from Amazon, Flipkart, and Myntra.

## Architecture

```
┌──────────────┐     POST /recommend     ┌─────────────────────────┐    Streamable HTTP    ┌──────────────────┐
│   React UI   │ ─────────────────────▶  │  MCP Client (this repo) │ ───────────────────▶  │   MCP Server     │
└──────────────┘                         │   ├─ Gemini Agent       │                       │  (product tools) │
                                         │   ├─ Redis Cache        │                       └──────────────────┘
                                         │   └─ .env config        │
                                         └─────────────────────────┘
```

### Agent Loop Flow
```
1. User prompt arrives at /recommend
2. Check Redis cache → return cached response if found
3. Connect to MCP Server via Streamable HTTP
4. Discover available tools (search_amazon, search_flipkart, search_myntra)
5. Map MCP tools → Gemini FunctionDeclarations
6. Send prompt + tools to Gemini
7. Gemini calls tools → Client executes them on MCP Server
8. Feed tool results back to Gemini → repeat until final answer
9. Cache & return the recommendation
```

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Build Tool | Poetry |
| AI Model | Google Gemini (via `google-genai` SDK) |
| MCP | MCP Python SDK (Client + Streamable HTTP) |
| Web Framework | FastAPI + Uvicorn |
| Data Models | Pydantic v2 |
| Caching | Redis (prompt-level SHA-256 hashing) |
| Logging | structlog (structured JSON) |
| Config | python-dotenv + environment variables |
| Container | Docker (multi-stage) |

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

## Environment Variables (`.env`)

| Variable | Default | Required | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | – | **Yes** | Google Gemini API key from [AI Studio](https://aistudio.google.com/apikey) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | No | Gemini model ID |
| `MCP_SERVER_URL` | `http://localhost:8000/mcp/sse` | No | MCP Server endpoint |
| `REDIS_HOST` | `localhost` | No | Redis hostname |
| `REDIS_PORT` | `6379` | No | Redis port |
| `REDIS_TTL` | `1800` | No | Response cache TTL (seconds) |
| `CLIENT_HOST` | `0.0.0.0` | No | Bind address |
| `CLIENT_PORT` | `8001` | No | Bind port |
| `GOOGLE_APPLICATION_CREDENTIALS` | – | No | GCP service account JSON (for Vertex AI) |
| `GOOGLE_CLOUD_PROJECT` | – | No | GCP project ID (for Vertex AI) |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | No | GCP region (for Vertex AI) |

### Gemini Access Options

| Method | When to Use | Config |
|---|---|---|
| **AI Studio API Key** | Development, prototyping | Set `GEMINI_API_KEY` |
| **Vertex AI** | Production, enterprise | Set `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT` |

## API

### `POST /recommend`
**Request:**
```json
{ "prompt": "I need the best wireless earbuds under ₹2000" }
```

**Response:**
```json
{
  "recommendation": "Based on my analysis across Amazon, Flipkart...",
  "products": [],
  "cached": false
}
```

### `GET /health`
```json
{ "status": "ok" }
```

## Project Structure

```
src/client/
├── __init__.py
├── main.py       # FastAPI entry point
├── config.py     # .env + environment settings
├── cache.py      # Redis prompt-level cache
├── models.py     # Pydantic models
└── agent.py      # Gemini + MCP agentic loop
```

## Testing

```bash
poetry run pytest tests/ -v
```

## License
MIT
