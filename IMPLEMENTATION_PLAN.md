# Implementation Plan – MCP Client

## Overview
Build the orchestration layer that receives user prompts from the UI, connects to the MCP Server to discover tools, feeds them to the Gemini model, executes tool calls, and returns curated product recommendations.

---

## Phase 1: Project Foundation ✅
- [x] Initialize Poetry project with `pyproject.toml`
- [x] Configure dependencies (mcp, fastapi, uvicorn, google-genai, redis, structlog)
- [x] Create package layout: `src/client/`
- [x] Create `Dockerfile` (two-stage build)
- [x] Create `.gitignore`, `README.md`

## Phase 2: Core Architecture ✅
- [x] `config.py` – Environment-based settings (MCP server URL, Gemini key, Redis)
- [x] `cache.py` – Prompt-level response caching with SHA-256 key hashing
- [x] `agent.py` – Gemini agentic loop with MCP tool discovery and execution
- [x] `main.py` – FastAPI app with `/recommend` endpoint and CORS

## Phase 3: Request / Response Models
- [ ] `models.py` – Pydantic models for `ChatRequest`, `ChatResponse`, `ProductRecommendation`
- [ ] Structured product data in response (not just raw text)
- [ ] Streaming response support (`StreamingResponse` + SSE)

## Phase 4: Advanced Agent Features
- [ ] `agent.py` enhancements:
  - [ ] Conversation history / multi-turn support
  - [ ] Token usage tracking
  - [ ] Configurable system prompts
  - [ ] Parallel tool execution when possible
- [ ] Error handling for Gemini API failures (retry, fallback)
- [ ] Timeout on MCP server connections

## Phase 5: Session & History Management
- [ ] `sessions.py` – In-memory or Redis-backed session store
- [ ] `/history` endpoint to retrieve past recommendations
- [ ] Session-scoped caching

## Phase 6: Observability
- [ ] Structured JSON logging
- [ ] `/health` and `/ready` endpoints (check MCP server + Redis connectivity)
- [ ] Request timing middleware

## Phase 7: Testing
- [ ] `tests/test_agent.py` – Mock Gemini + MCP and verify the loop
- [ ] `tests/test_cache.py` – Cache integration tests
- [ ] `tests/test_api.py` – Full endpoint integration tests

## Phase 8: Deployment
- [ ] Shared `docker-compose.yml`
- [ ] GitHub Actions CI skeleton

---

## File Structure (Target)
```
ecommerce-best-products-client/
├── src/
│   └── client/
│       ├── __init__.py
│       ├── main.py          # FastAPI entry point
│       ├── config.py         # Environment settings
│       ├── cache.py          # Redis prompt cache
│       ├── models.py         # Pydantic models
│       ├── agent.py          # Gemini + MCP agentic loop
│       └── sessions.py       # Session management (future)
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_cache.py
│   └── test_api.py
├── pyproject.toml
├── Dockerfile
├── .gitignore
└── README.md
```
