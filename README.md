# E-Commerce Best Products – MCP Client

An MCP Client that orchestrates **Gemini** and the MCP Server to deliver AI-powered product recommendations.

## Architecture

```
┌──────────────┐       POST /recommend       ┌──────────────────────┐       MCP/SSE       ┌──────────────────┐
│   React UI   │ ──────────────────────────▶  │  MCP Client (this)   │ ──────────────────▶ │   MCP Server     │
└──────────────┘                              │   ├─ Gemini Agent    │                     │  (product tools) │
                                              │   └─ Redis Cache     │                     └──────────────────┘
                                              └──────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.12+
- Poetry
- A Gemini API key (`GEMINI_API_KEY`)
- The MCP Server running at a known URL

### Install & Run
```bash
poetry install
export GEMINI_API_KEY="your-key"
poetry run uvicorn client.main:app --reload --port 8001
```

### Docker
```bash
docker build -t mcp-client .
docker run -p 8001:8001 -e GEMINI_API_KEY=your-key mcp-client
```

### Environment Variables
| Variable | Default | Description |
|---|---|---|
| `MCP_SERVER_URL` | `http://localhost:8000/mcp` | MCP Server SSE endpoint |
| `GEMINI_API_KEY` | *(required)* | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model to use |
| `REDIS_HOST` | `localhost` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `CLIENT_HOST` | `0.0.0.0` | Bind address |
| `CLIENT_PORT` | `8001` | Bind port |

## API

### `POST /recommend`
**Request:**
```json
{ "prompt": "I need the best wireless earbuds under ₹2000" }
```

**Response:**
```json
{ "recommendation": "Based on my analysis across... (Gemini response)" }
```

## License
MIT
