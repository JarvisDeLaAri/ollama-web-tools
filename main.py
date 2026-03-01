#!/usr/bin/env python3
"""
OllamaWebTools - internal localhost API that proxies Ollama web_search/web_fetch.
"""

import os
import logging

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load env before anything else
load_dotenv()

# Config from env
PORT = int(os.getenv("PORT", "10021"))
HOST = os.getenv("HOST", "127.0.0.1")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()

OLLAMA_WEB_SEARCH_URL = "https://ollama.com/api/web_search"
OLLAMA_WEB_FETCH_URL = "https://ollama.com/api/web_fetch"
HTTP_TIMEOUT = 30.0

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ollama-web-tools")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    count: int = Field(default=5, ge=1, le=10, description="Number of results")


class SearchResult(BaseModel):
    title: str
    url: str
    content: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class FetchRequest(BaseModel):
    url: str = Field(..., min_length=1, description="URL to fetch")
    max_chars: int = Field(default=5000, ge=100, le=50000)


class FetchResponse(BaseModel):
    url: str
    title: str
    content: str
    links: list[str] = []


class HealthResponse(BaseModel):
    status: str
    ollama_status: str
    key_configured: bool


def build_auth_headers() -> dict[str, str]:
    if not OLLAMA_API_KEY:
        raise ValueError("OLLAMA_API_KEY not set")
    return {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json",
    }


async def check_local_ollama() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


async def real_web_search(query: str, count: int = 5) -> list[SearchResult]:
    payload = {"query": query, "max_results": count}
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.post(
            OLLAMA_WEB_SEARCH_URL,
            headers=build_auth_headers(),
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            content=item.get("content", ""),
        )
        for item in data.get("results", [])
    ]


async def real_web_fetch(url: str) -> FetchResponse:
    payload = {"url": url}
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.post(
            OLLAMA_WEB_FETCH_URL,
            headers=build_auth_headers(),
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    return FetchResponse(
        url=url,
        title=data.get("title", ""),
        content=data.get("content", ""),
        links=[str(x) for x in data.get("links", []) if isinstance(x, str)],
    )


app = FastAPI(
    title="OllamaWebTools",
    description="Local proxy API for Ollama web_search/web_fetch",
    version="2.1.0",
)


@app.get("/", response_model=dict)
async def root():
    return {
        "service": "OllamaWebTools",
        "version": "2.1.0",
        "docs": "/docs",
        "endpoints": ["/search", "/fetch", "/health"],
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        ollama_status="connected" if await check_local_ollama() else "disconnected",
        key_configured=bool(OLLAMA_API_KEY),
    )


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    logger.info("Search: %s", request.query)
    try:
        results = await real_web_search(request.query, request.count)
        return SearchResponse(query=request.query, results=results)
    except httpx.HTTPStatusError as e:
        logger.error("Ollama API error: %s - %s", e.response.status_code, e.response.text)
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text) from e
    except Exception as e:
        logger.error("Search failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/fetch", response_model=FetchResponse)
async def fetch(request: FetchRequest):
    logger.info("Fetch: %s", request.url)
    try:
        result = await real_web_fetch(request.url)
        if len(result.content) > request.max_chars:
            result.content = result.content[: request.max_chars] + "..."
        return result
    except httpx.HTTPStatusError as e:
        logger.error("Ollama API error: %s - %s", e.response.status_code, e.response.text)
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text) from e
    except Exception as e:
        logger.error("Fetch failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting OllamaWebTools v2.1.0 on %s:%s", HOST, PORT)
    logger.info("API key configured: %s", bool(OLLAMA_API_KEY))
    uvicorn.run(app, host=HOST, port=PORT)
