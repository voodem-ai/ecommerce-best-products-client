"""FastAPI application – exposes the /recommend endpoint for the React UI."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from client.agent import run_agent
from client.cache import cache_get_recommendation, cache_set_recommendation, close_redis
from client.config import settings

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Incoming user prompt."""
    prompt: str


class ChatResponse(BaseModel):
    """Outgoing recommendation from Gemini."""
    recommendation: str


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
    return {"status": "ok"}


@app.post("/recommend", response_model=ChatResponse)
async def recommend(request: ChatRequest):
    """Receive a user prompt, run the Gemini + MCP agent, return the recommendation."""
    log.info("recommend_request", prompt=request.prompt[:80])

    # Check cache first
    cached = await cache_get_recommendation(request.prompt)
    if cached:
        log.info("recommend_cache_hit")
        return ChatResponse(recommendation=cached)

    # Run the agentic loop
    result = await run_agent(request.prompt)

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
