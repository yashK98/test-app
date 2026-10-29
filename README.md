
import hashlib
import os
import threading
import time
from collections import OrderedDict

import numpy as np
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Use one process for this in-memory cache.
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

CACHE_MAX_SIZE = 10_000
CACHE_TTL_SECONDS = 3600
SIMILARITY_THRESHOLD = float(
    os.getenv("SIMILARITY_THRESHOLD", "0.95")
)

LAYA_URL = os.environ["LAYA_URL"]

# OrderedDict maintains LRU order.
# Key: exact text hash
# Value: text hash, embedding, sentiment, expiration
cache = OrderedDict()
cache_lock = threading.RLock()


class SentimentRequest(BaseModel):
    subject: str
    body: str


def prepare_text(subject: str, body: str) -> str:
    subject = " ".join(subject.split())
    body = " ".join(body.split())
    return f"Subject: {subject}\nBody: {body}"


def make_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_exact(key: str):
    now = time.monotonic()

    with cache_lock:
        entry = cache.get(key)
        if entry is None:
            return None

        if entry["expires_at"] <= now:
            del cache[key]
            return None

        cache.move_to_end(key)
        return entry["sentiment"]


def get_semantic(embedding: np.ndarray):
    now = time.monotonic()
    best_key = None
    best_score = -1.0

    with cache_lock:
        # Remove expired entries.
        expired = [
            key for key, entry in cache.items()
            if entry["expires_at"] <= now
        ]
        for key in expired:
            del cache[key]

        # All embeddings are normalized, so dot product
        # is cosine similarity.
        for key, entry in cache.items():
            score = float(np.dot(embedding, entry["embedding"]))

            if score > best_score:
                best_score = score
                best_key = key

        if (
            best_key is not None
            and best_score >= SIMILARITY_THRESHOLD
        ):
            cache.move_to_end(best_key)
            return cache[best_key]["sentiment"]

    return None


def put_cache(key: str, embedding: np.ndarray, sentiment: str):
    with cache_lock:
        cache[key] = {
            "embedding": embedding.copy(),
            "sentiment": sentiment,
            "expires_at": time.monotonic() + CACHE_TTL_SECONDS,
        }
        cache.move_to_end(key)

        while len(cache) > CACHE_MAX_SIZE:
            cache.popitem(last=False)


def call_laya(text: str) -> str:
    # Adapt this payload and response parsing to your Laya API.
    response = requests.post(
        LAYA_URL,
        json={"text": text},
        timeout=15,
    )
    response.raise_for_status()

    sentiment = response.json()["sentiment"]
    allowed = {"HAPPY", "NEUTRAL", "ANGRY", "DISAPPOINTED"}

    if sentiment not in allowed:
        raise ValueError("Unexpected sentiment returned by Laya")

    return sentiment


@app.post("/sentiment")
def analyze_sentiment(request: SentimentRequest):
    text = prepare_text(request.subject, request.body)
    key = make_key(text)

    # 1. Exact match: no embedding or Laya call needed.
    sentiment = get_exact(key)
    if sentiment is not None:
        return {"sentiment": sentiment, "cache": "exact_hit"}

    # 2. Semantic match.
    embedding = model.encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype(np.float32)

    sentiment = get_semantic(embedding)
    if sentiment is not None:
        return {"sentiment": sentiment, "cache": "semantic_hit"}

    # 3. Cache miss: call Laya.
    try:
        sentiment = call_laya(text)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Sentiment provider request failed",
        ) from exc

    # Cache only successful, validated responses.
    put_cache(key, embedding, sentiment)

    return {"sentiment": sentiment, "cache": "miss"}
