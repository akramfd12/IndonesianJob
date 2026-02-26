# IndonesianJob

FastAPI service with an LLM agent to search Indonesian job vacancies via RAG (semantic search) and SQL queries. Designed to power job recommendation and search workflows.

## Overview

**IndonesianJob** combines LangChain's agent framework with Qdrant vector search and SQL analytics to provide intelligent job discovery. The agent understands natural language queries ("Find data analyst positions in Jakarta with salary > 7M") and automatically chooses the right tool (RAG for search, SQL for analytics) to generate accurate responses.

## Features

- 🤖 **LLM-powered agent** — OpenAI GPT + LangChain agent orchestration
- 🔍 **RAG-based search** — Qdrant vector DB for semantic job matching
- 📊 **Structured results** — Job title, company, salary, location, work type, etc.
- 📈 **SQL analytics** — Support for aggregate queries (statistics, counts, trends)
- 🚀 **REST API** — FastAPI with auto-doc generation at `/docs`
- ⚡ **Production-ready** — Error handling, logging, CORS support

## Setup

### Prerequisites
- Python 3.10+
- Qdrant instance (local or cloud)
- OpenAI API key
- Hugging Face token (for embeddings)
- Mixbread API key (alternative embedding provider)

### 1. Qdrant Setup (Local)

If you don't have Qdrant running, start it locally:

```bash
# Using Docker
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

Qdrant will be available at `http://localhost:6333`.

### 2. Clone & Environment

1. **Clone repository:**
   ```bash
   git clone <repo-url>
   cd IndonesianJob
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Variables

Create a `.env` file or export variables:

```bash
# Required
export OPENAI_API_KEY=sk-your-key-here
export QDRANT_URL=http://localhost:6333
export QDRANT_COLLECTION_NAME=jobs

# Optional (alternative embeddings providers)
export HF_TOKEN=hf_your-huggingface-token
export MIXBREAD_API=your-mixbread-key

# Optional
export PORT=8080
export LOG_LEVEL=INFO
```

### 4. Initialize & Run

```bash
# If needed, initialize Qdrant collection with job data
python db/qdrant.py  # or your init script

# Start the server
uvicorn api.routes:app --host 0.0.0.0 --port 8080 --reload
```

Visit **http://localhost:8080/docs** for interactive API explorer.

## API Documentation

### Endpoints

#### `POST /chat` — Job Search & Query
Main endpoint for querying jobs or analytics.

**Request Schema:**
```json
{
  "user_input": "string (required) — natural language query",
  "top_k": "integer (default: 5) — max results to return"
}
```

**Example Request:**
```json
{
  "user_input": "Cari posisi Data Analyst di Jakarta dengan gaji minimal 7 juta rupiah",
  "top_k": 5
}
```

**Example Response:**
```json
{
  "response": "Berikut 5 lowongan Data Analyst di Jakarta yang sesuai dengan kriteria Anda...",
  "source": [
    {
      "job_title": "Data Analyst",
      "company_name": "PT ABC Indonesia",
      "location": "Jakarta Selatan",
      "work_type": "Full time",
      "job_description": "Analyze sales data, create dashboards...",
      "salary": "Rp 7.5M - 10M",
      "salary_min": 7500000,
      "salary_max": 10000000,
      "relevance_score": 0.95
    }
  ]
}
```

#### `GET /` — Welcome
Returns available endpoints and service status.

```bash
curl http://localhost:8080/
```

#### `GET /health` — Health Check
Verify service is running and all credentials are valid.

```bash
curl http://localhost:8080/health
```

#### `GET /history` — Chat History
Retrieve conversation history (placeholder for future implementation).

```bash
curl http://localhost:8080/history
```

#### `POST /reset` — Clear History
Reset chat history (placeholder for future implementation).

```bash
curl -X POST http://localhost:8080/reset
```

### Query Examples

**Search by job title:**
```
"Cari lowongan Software Engineer di Indonesia"
```

**Filter by salary & location:**
```
"Data Analyst di Jakarta dengan gaji 8 juta keatas"
```

**Analytics query:**
```
"Berapa banyak lowongan full-time di Jakarta?"
```

## Architecture

### Agent Flow

```
User Query ("/chat")
    ↓
[chatbot_agent] — LLM + LangChain
    ↓
    ├─→ Is this a job search? → [rag_agent]
    │    ├─→ Embed query
    │    ├─→ Search Qdrant
    │    └─→ Return top-k jobs
    │
    └─→ Is this an analytics query? → [sql_agent]
        ├─→ Parse SQL intent
        ├─→ Query SQLite/DB
        └─→ Return aggregates

    ↓
[parse_tool_results] — Convert to JobResultResponse
    ↓
Response (AI text + structured jobs)
```

### Code Organization

| Directory | Purpose |
|-----------|---------|
| `agents/` | Agent orchestration & tool definitions |
| `services/` | Job matching, embeddings, business logic |
| `db/` | Qdrant & SQLite integration |
| `api/` | FastAPI routes & request/response schemas |
| `data/` | Job dataset (JSONL) |

### Key Files

| File | Role |
|------|------|
| `main.py` | Entry point; runs Uvicorn |
| `api/routes.py` | All API endpoints & CORS config |
| `api/schemas.py` | Pydantic models (`ChatRequest`, `ChatResponse`, `JobResultResponse`) |
| `agents/chatbot_agent.py` | LLM agent creation & invocation |
| `agents/rag_agent.py` | Vector search tool (Qdrant) |
| `agents/sql_agent.py` | SQL analytics tool |
| `services/embeddings_services.py` | Embedding generation & caching |
| `db/qdrant.py` | Qdrant client & operations |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `No module named 'fastapi'` | Activate venv: `.\.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac) |
| `ConnectionError: Qdrant` | Ensure Qdrant is running; check `QDRANT_URL` is correct |
| Empty `source` in response | Agent may not have triggered RAG tool; check logs & enable debug logging |
| `OpenAI API rate limit` | Add retry logic or increase rate limit tier |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` or check Python version (3.10+) |
| Agent returns generic response | Verify LLM system prompt & agent tools are functioning via logs |

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or via environment:
```bash
export LOG_LEVEL=DEBUG
```

## Development

### Project Dependencies

Key packages (see `requirements.txt`):
- `fastapi` — REST framework
- `uvicorn` — ASGI server
- `langchain` — Agent framework
- `qdrant-client` — Vector DB client
- `openai` — LLM API
- `pydantic` — Data validation

### Running in Development

```bash
# With auto-reload
uvicorn api.routes:app --reload --host 0.0.0.0 --port 8080

# With debug logging
LOG_LEVEL=DEBUG uvicorn api.routes:app --reload
```

### Testing

Run endpoint manually via curl:

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Cari lowongan Python di Jakarta", "top_k": 3}'
```

Or use the interactive docs at `http://localhost:8080/docs`.

### Adding a New Tool

1. Create tool function in `agents/new_tool.py`
2. Register in `agents/tools.py`
3. Add to `chatbot_agent.py` tool list
4. Update agent system prompt to describe when to use it
5. Test via `/chat` endpoint

## Contributing

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make changes** & follow code style (PEP 8)
4. **Test** your changes (manually or add unit tests)
5. **Commit**: `git commit -am 'Add my feature'`
6. **Push**: `git push origin feature/my-feature`
7. **Open a PR** with description of changes

## Performance & Scaling

- **API responses** typically take 3-5s (LLM inference + Qdrant search)
- **Caching** embeddings can reduce latency by ~50%
- **Load balancing** with multiple instances recommended for production
- **Async database calls** can be optimized in `services/`

## Production Checklist

- [ ] Use production-grade LLM (gpt-4-turbo or similar)
- [ ] Set up Qdrant cluster or managed service
- [ ] Enable authentication (API key, OAuth)
- [ ] Configure logging & monitoring (Sentry, DataDog)
- [ ] Add rate limiting
- [ ] Use environment-specific configs
- [ ] Set `debug=False` in FastAPI
- [ ] Run tests before deployment
- [ ] Document custom tools & queries

## Resources

- [LangChain Docs](https://python.langchain.com/)
- [Qdrant Vector Search](https://qdrant.tech/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/)

## Roadmap

### Phase 1 (MVP) ✅
- [x] Basic RAG search
- [x] LLM agent orchestration
- [x] FastAPI endpoints
- [x] Qdrant integration

### Phase 2 (Planned)
- [ ] User authentication & API keys
- [ ] Chat history persistence
- [ ] Redis caching for embeddings
- [ ] Unit & integration tests
- [ ] Docker & docker-compose

### Phase 3 (Future)
- [ ] Multi-language support (English, Chinese, etc.)
- [ ] Advanced filtering (skills, benefits, work arrangement)
- [ ] Job recommendation algorithm
- [ ] Admin dashboard
- [ ] Analytics & reporting

## License

MIT License — see [LICENSE](LICENSE) file.
