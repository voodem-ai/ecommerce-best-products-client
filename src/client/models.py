"""Pydantic models for API request/response and internal data."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming user prompt from the UI."""

    prompt: str = Field(..., min_length=1, max_length=1000, description="User search prompt")


class ProductItem(BaseModel):
    """A single product in the recommendation response."""

    name: str
    price: float
    rating: float
    buyers: int
    source: str
    url: str
    image_url: str | None = None


class ChatResponse(BaseModel):
    """Outgoing recommendation from the Gemini agent."""

    recommendation: str = Field(..., description="Gemini-generated recommendation text (markdown)")
    products: list[ProductItem] = Field(default_factory=list, description="Structured product data if extracted")
    cached: bool = Field(False, description="Whether this response was served from cache")
