"""FastAPI application – exposes the /recommend endpoint for the React UI."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from client.agent import run_agent
from client.cache import cache_get_recommendation, cache_set_recommendation, close_redis
from client.config import settings
from client.models import ChatRequest, ChatResponse

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(application: FastAPI):
    log.info("client_starting", port=settings.CLIENT_PORT)
    yield
    await close_redis()
    log.info("client_stopped")


app = FastAPI(
    title="E-Commerce Best Products – MCP Client",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Liveness probe."""
    return {"status": "ok"}


@app.post("/recommend", response_model=ChatResponse)
async def recommend(request: ChatRequest):
    """Receive a user prompt, run the Gemini + MCP agent, return the recommendation."""
    log.info("recommend_request", prompt=request.prompt[:80])

    # Check cache first
    cached = await cache_get_recommendation(request.prompt)
    if cached:
        log.info("recommend_cache_hit")
        return ChatResponse(recommendation=cached, cached=True)

    try:
        result = await run_agent(request.prompt)
    except Exception as exc:
        log.error("agent_error", error=str(exc))
        raise HTTPException(status_code=502, detail=f"Agent error: {exc}") from exc

    # Cache the result
    await cache_set_recommendation(request.prompt, result)

    return ChatResponse(recommendation=result)


# ---------------------------------------------------------------------------
# Run directly: python -m client.main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "client.main:app",
        host=settings.CLIENT_HOST,
        port=settings.CLIENT_PORT,
        reload=True,
    )
