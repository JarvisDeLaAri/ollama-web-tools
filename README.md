# OllamaWebTools

## Setup for Human:

1. goto `https://ollama.com/settings/keys` and create api key (NOT device key!)
2. give this repo to your OpenClaw and tell him to duplicate and make it work, while giving him the key
3. give any agent to read `how-to-use-for-ai.md`


## About


Localhost API wrapper for **real** Ollama Web Search / Web Fetch.

- Runs locally (default `127.0.0.1:10021`)
- Calls Ollama cloud endpoints:
  - `https://ollama.com/api/web_search`
  - `https://ollama.com/api/web_fetch`
- Auth via `OLLAMA_API_KEY` in `.env`

## References

- OpenClaw web tools docs: https://docs.openclaw.ai/tools/web
- Ollama web search docs: https://docs.ollama.com/capabilities/web-search

## Quick Start

```bash
cd ollama-web-tools
python3 -m pip install --break-system-packages -r requirements.txt
cp .env.example .env
# edit .env and set OLLAMA_API_KEY
python3 main.py
```

## API

Base URL:

```text
http://127.0.0.1:10021
```

### `GET /health`
Returns local status and whether API key is configured.

### `POST /search`
Request:

```json
{
  "query": "latest youtube trends",
  "count": 5
}
```

Response:

```json
{
  "query": "latest youtube trends",
  "results": [
    {
      "title": "...",
      "url": "https://...",
      "content": "..."
    }
  ]
}
```

### `POST /fetch`
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

## Notes

- `.env` is ignored by git.
- `OLLAMA_API_KEY` must be a real key from `ollama.com/settings/keys`.
- If port `10021` is already used, set `PORT` in `.env`.
