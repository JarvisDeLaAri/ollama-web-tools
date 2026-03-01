# How to Use OllamaWebTools (for AI agents)

This service provides **real** web search/fetch via Ollama cloud APIs.

## Base URL

`http://127.0.0.1:10021`

## Endpoints

### 1) Search

`POST /search`

Request:

```json
{
  "query": "latest AI news",
  "count": 5
}
```

Response:

```json
{
  "query": "latest AI news",
  "results": [
    {
      "title": "...",
      "url": "https://...",
      "content": "..."
    }
  ]
}
```

### 2) Fetch

`POST /fetch`

Request:

```json
{
  "url": "https://example.com",
  "max_chars": 5000
}
```

Response:

```json
{
  "url": "https://example.com",
  "title": "...",
  "content": "...",
  "links": ["https://..."]
}
```

### 3) Health

`GET /health`

Response:

```json
{
  "status": "healthy",
  "ollama_status": "connected",
  "key_configured": true,
  "model": "kimi-k2.5:cloud"
}
```

## Quick curl

```bash
curl -s http://127.0.0.1:10021/health

curl -s -X POST http://127.0.0.1:10021/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"latest youtube trends","count":5}'

curl -s -X POST http://127.0.0.1:10021/fetch \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://ollama.com","max_chars":1500}'
```

## References

- https://docs.openclaw.ai/tools/web
- https://docs.ollama.com/capabilities/web-search
