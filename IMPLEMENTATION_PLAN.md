# Implementation Plan – MCP Client

## Overview
Build the orchestration layer that receives user prompts from the UI, connects to the MCP Server to discover tools, feeds them to Google Gemini, executes tool calls, and returns curated product recommendations.

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
- [x] `agent.py` – Gemini agentic loop over standard `mcp.client.sse` Stream
- [x] `agent.py` – Smart auto-fallback between AI Studio API Keys and Vertex AI Google credentials
- [x] `main.py` – FastAPI app with `/recommend` endpoint and CORS

## Phase 3: Request / Response Models ✅
- [x] `models.py` – Pydantic models for `ChatRequest`, `ChatResponse`, `ProductItem`
- [x] Structured product data in response
- [ ] Streaming response support (`StreamingResponse` + SSE)

## Phase 4: Gemini & Google Access Setup ✅
- [x] `.env.example` – Template with `GEMINI_API_KEY`, Google Cloud credentials
- [x] `python-dotenv` integration – Auto-loads `.env` on startup
- [x] `GEMINI_API_KEY` configuration – For Google AI Studio access
- [x] `GEMINI_MODEL` selection – Configurable model (`gemini-2.5-flash`, `gemini-2.5-pro`)
- [x] `GOOGLE_APPLICATION_CREDENTIALS` – For Vertex AI enterprise access (optional)
- [x] `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` – GCP Vertex AI config (optional)
- [x] `SKILLS.md` – Complete skills documentation including Gemini integration details

## Phase 5: Advanced Agent Features
- [ ] Conversation history / multi-turn support
- [ ] Token usage tracking
- [ ] Configurable system prompts
- [ ] Parallel tool execution when possible
- [ ] Error handling for Gemini API failures (retry, fallback)
- [ ] Timeout on MCP server connections

## Phase 6: Testing ✅
- [x] `tests/test_api.py` – API endpoint tests (4 tests)
- [ ] `tests/test_agent.py` – Mock Gemini + MCP agent tests
- [ ] `tests/test_cache.py` – Cache integration tests

## Phase 7: Deployment ✅
- [x] Shared `docker-compose.yml`
- [x] Environment variable documentation in README
- [ ] GitHub Actions CI skeleton

---

## File Structure
```
ecommerce-best-products-client/
├── src/client/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py       ← .env loading + Gemini + Google Cloud config
│   ├── cache.py
│   ├── models.py
│   └── agent.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .env.example        ← NEW: GEMINI_API_KEY, Google Cloud settings
├── SKILLS.md           ← NEW: skills documentation
├── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── Dockerfile
├── .gitignore
└── README.md
```
