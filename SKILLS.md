# Skills – MCP Client

Technical skills and competencies required to develop, maintain, and extend this project.

---

## Core Skills

### Python Development
- **Python 3.12+** – Modern Python with type hints, async/await, and union types
- **Poetry** – Dependency management, virtual environments, build system
- **Pydantic v2** – Request/response models, data validation

### MCP (Model Context Protocol)
- **MCP Client SDK** – Session management, tool discovery, tool execution
- **Streamable HTTP Transport** – Connecting to remote MCP servers
- **Tool Schema Mapping** – Converting MCP tool schemas to Gemini function declarations

### Gemini AI & Google Integration
- **Google GenAI SDK** (`google-genai`) – Model initialization, content generation
- **Gemini API Key Authentication** – Using `GEMINI_API_KEY` from AI Studio
- **Function Calling** – Registering tools with Gemini and processing `FunctionCall` responses
- **Multi-turn Conversations** – Building `Content` arrays with user, model, and tool results
- **Agentic Loops** – Iterative tool-calling until Gemini produces a final text answer
- **Vertex AI (Optional)** – Using `GOOGLE_APPLICATION_CREDENTIALS` for enterprise Gemini access
- **System Instructions** – Configuring Gemini's behavior via `system_instruction` parameter

### Web Framework
- **FastAPI** – REST API design, CORS middleware, error handling, lifespan
- **Uvicorn** – ASGI server, hot-reload in development

### Caching
- **Redis** – Async client, prompt-level response caching
- **SHA-256 Hashing** – Deterministic cache keys for user prompts
- **Graceful degradation** – Cache failures don't crash the app

---

## Google & Cloud Skills

### Google AI Studio
- **API Key Management** – Obtaining and securing `GEMINI_API_KEY`
- **Model Selection** – Choosing between `gemini-2.5-flash`, `gemini-2.5-pro`, etc.
- **Rate Limits** – Understanding and handling Gemini API quota limits

### Google Cloud Platform (Optional – Vertex AI)
- **Service Account Authentication** – `GOOGLE_APPLICATION_CREDENTIALS` JSON key file
- **GCP Project & Location** – `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`
- **Vertex AI Gemini** – Enterprise-grade Gemini via Vertex AI endpoints

### Environment Configuration
- **python-dotenv** – Loading `.env` files for local development
- **12-Factor App** – Configuration via environment variables

---

## DevOps & Infrastructure

### Docker
- **Multi-stage builds** – Optimized production images
- **Poetry in Docker** – Layer caching for dependencies
- **Environment variable injection** – Secrets at runtime, not build time

### Kubernetes & Deployment
- **Helm** – Managing deployments using a centralized Helm chart (`helm/ecommerce-client/`)
- **Internal Networking** – Using a `ClusterIP` service to restrict public internet access and force traffic through the UI reverse proxy.

### Docker Compose
- **Service dependencies** – Correct startup ordering
- **Environment files** – `.env` file loading in compose

### Version Control
- **Git & GitHub** – Organization repositories, branch management

---

## Testing

- **pytest** – Test runner
- **FastAPI TestClient** – Synchronous API endpoint testing
- **unittest.mock** – `AsyncMock`, `patch` for mocking the agent and cache
- **Test coverage** – Health endpoint, validation errors, cache hits, agent responses

---

## Architecture Patterns

| Pattern | Usage |
|---|---|
| **Agent Loop** | Gemini calls tools → execute on MCP server → feed results back → repeat until final answer |
| **Gateway/BFF** | Client acts as Backend-for-Frontend between the UI and MCP Server |
| **Cache-Aside** | SHA-256 hashed prompt → Redis lookup → agent on miss |
| **Adapter** | MCP tool schemas → Gemini `FunctionDeclaration` mapping |
| **12-Factor Config** | All config via env vars + `.env` file |
