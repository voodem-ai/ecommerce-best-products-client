"""Application configuration loaded from environment variables."""

import os


class Settings:
    """Client configuration."""

    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "1800"))  # 30 min
    CLIENT_HOST: str = os.getenv("CLIENT_HOST", "0.0.0.0")
    CLIENT_PORT: int = int(os.getenv("CLIENT_PORT", "8001"))


settings = Settings()
