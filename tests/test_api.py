"""Tests for the /recommend API endpoint."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from client.main import app

client = TestClient(app)


def test_health_endpoint():
    """GET /health should return 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recommend_empty_prompt_returns_422():
    """POST /recommend with empty prompt should return 422."""
    response = client.post("/recommend", json={"prompt": ""})
    assert response.status_code == 422


@patch("client.main.cache_get_recommendation", new_callable=AsyncMock, return_value=None)
@patch("client.main.cache_set_recommendation", new_callable=AsyncMock)
@patch("client.main.run_agent", new_callable=AsyncMock, return_value="Here are the best products...")
def test_recommend_success(mock_agent, mock_cache_set, mock_cache_get):
    """POST /recommend with valid prompt should return agent response."""
    response = client.post("/recommend", json={"prompt": "best wireless earbuds"})
    assert response.status_code == 200
    data = response.json()
    assert "recommendation" in data
    assert data["recommendation"] == "Here are the best products..."
    assert data["cached"] is False


@patch("client.main.cache_get_recommendation", new_callable=AsyncMock, return_value="Cached recommendation")
def test_recommend_cache_hit(mock_cache):
    """When cache has data, should return cached response."""
    response = client.post("/recommend", json={"prompt": "best laptop"})
    assert response.status_code == 200
    data = response.json()
    assert data["cached"] is True
    assert data["recommendation"] == "Cached recommendation"
