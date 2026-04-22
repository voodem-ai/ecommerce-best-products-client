# Implementation Plan – MCP Client

## Overview
Build the orchestration layer that receives user prompts from the React UI, connects to the MCP Server via SSE, discovers tools, feeds them to Google Gemini, executes tool calls in parallel, and returns curated product recommendations in an HTML tabular format.

---

## Phase 1: Project Foundation ✅
- [x] Initialize Poetry project with `pyproject.toml`
- [x] Configure dependencies (mcp, fastapi, uvicorn, google-genai, redis, structlog, python-dotenv)
- [x] Create package layout: `src/client/`
- [x] Create `Dockerfile` (two-stage build)
- [x] Create `.gitignore`, `README.md`

## Phase 2: Core Architecture ✅
- [x] `config.py` – Environment-based settings with `.env` file support via python-dotenv
- [x] `cache.py` – Prompt-level response caching with SHA-256 key hashing
- [x] `agent.py` – Full Gemini agentic loop (max 5 rounds) using `mcp.client.sse.sse_client`
- [x] `agent.py` – `GEMINI_API_KEY` prioritised over Vertex AI (avoids stray GCP billing errors)
- [x] `main.py` – FastAPI app with `/recommend` and `/health` endpoints + CORS

## Phase 3: MCP SSE Transport ✅
- [x] Client connects to MCP Server via `sse_client(MCP_SERVER_URL)` from `mcp.client.sse`
- [x] `MCP_SERVER_URL` must point to `/mcp/sse` (e.g. `http://localhost:8000/mcp/sse`)
- [x] Fixed 404 errors caused by old `MCP_SERVER_URL=http://localhost:8000/mcp` default
- [x] MCP tools auto-discovered via `session.list_tools()` and mapped to Gemini `FunctionDeclaration`

## Phase 4: Parallel Tool Execution ✅
- [x] Tool calls from Gemini (`function_calls`) executed concurrently via `asyncio.gather`
- [x] Each `execute_tool(fc)` coroutine runs independently — Amazon, Flipkart, Myntra fire at once
- [x] Per-tool error isolation: failures return `{"error": "..."}` without crashing the whole round
- [x] Reduces total response time from ~90s sequential → ~30s parallel

## Phase 5: Response Format ✅
- [x] Gemini `system_instruction` mandates **HTML tabular output** for Top 3 products
- [x] Table class `styled-table` rendered with premium CSS in the React UI
- [x] Columns: Rank, Product Name, Price, Link (`<a href>` to actual product), Reason for ranking
- [x] `<table>` output as single continuous string — no newlines that break `dangerouslySetInnerHTML`

## Phase 6: Gemini & Google Access ✅
- [x] `.env.example` – Template with `GEMINI_API_KEY`, Google Cloud credentials
- [x] `GEMINI_API_KEY` checked first; Vertex AI only used if API key absent/blank
- [x] `GEMINI_MODEL` configurable (`gemini-2.5-flash` default)
- [x] `SKILLS.md` – Complete skills documentation including Gemini integration

## Phase 7: Advanced Agent Features (Partial)
- [ ] Conversation history / multi-turn support
- [ ] Token usage tracking
- [ ] Configurable system prompts via env var
- [x] Parallel tool execution using `asyncio.gather`
- [ ] Retry/backoff on Gemini API failures
- [ ] Configurable timeout on MCP server connections

## Phase 8: Testing ✅
- [x] `tests/test_api.py` – API endpoint tests (4 tests)
- [ ] `tests/test_agent.py` – Mock Gemini + MCP agent unit tests
- [ ] `tests/test_cache.py` – Cache integration tests

## Phase 9: Deployment ✅
- [x] Shared `docker-compose.yml`
- [x] Environment variable documentation in README
- [x] GitHub Actions CI pipeline with Helm deployment (`helm/ecommerce-client/`)
- [x] Internal Networking (ClusterIP) to secure the API

---

## File Structure
```
ecommerce-best-products-client/
├── src/client/
│   ├── __init__.py
│   ├── main.py         ← FastAPI app with /recommend endpoint
│   ├── config.py       ← .env loading + Gemini + Google Cloud config
│   ├── cache.py        ← SHA-256 prompt-level Redis cache
│   ├── models.py       ← Pydantic request/response models
│   └── agent.py        ← Gemini agentic loop + parallel MCP tool calls
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── helm/
│   └── ecommerce-client/  ← Helm chart deployment files
├── .env                ← Local config (not committed)
├── .env.example        ← Template
├── SKILLS.md
├── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── Dockerfile
├── .gitignore
└── README.md
```
