"""Application configuration loaded from .env file and environment variables."""

import os

from dotenv import load_dotenv

# Load .env file from project root (auto-discovers .env in CWD or parents)
load_dotenv()


class Settings:
    """Client configuration.

    Values are read from environment variables. Place a `.env` file in the
    project root for local development (see `.env.example`).
    """

    # --- Gemini AI (REQUIRED) ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # --- Google Cloud (optional – Vertex AI) ---
    GOOGLE_APPLICATION_CREDENTIALS: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_CLOUD_PROJECT: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    # --- MCP Server ---
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp/sse")

    # --- Redis Cache ---
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "1800"))  # 30 min

    # --- Client Server ---
    CLIENT_HOST: str = os.getenv("CLIENT_HOST", "0.0.0.0")
    CLIENT_PORT: int = int(os.getenv("CLIENT_PORT", "8001"))


settings = Settings()
