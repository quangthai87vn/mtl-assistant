import os
from typing import List, Optional, Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np

# sentence-transformers
from sentence_transformers import SentenceTransformer

# torch is optional but used for device detection
try:
    import torch
except Exception:
    torch = None


def pick_device() -> str:
    """
    Cross-platform device picker.
    - macOS native: mps
    - linux/windows: cuda
    - fallback: cpu

    NOTE: In Docker on macOS, MPS is NOT available (Linux container) => cpu.
    """
    forced = os.getenv("DEVICE", "").strip().lower()
    if forced:
        return forced

    if torch is None:
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"

    # macOS native only (not inside Linux containers)
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"

    return "cpu"


MODEL_ID = os.getenv("MODEL_ID", "dangvantuan/vietnamese-document-embedding")
DEVICE = pick_device()
MAX_BATCH = int(os.getenv("MAX_BATCH", "64"))

app = FastAPI(title="Vietnamese Embedding Server", version="1.0.0")

# Load once

model = SentenceTransformer(
    MODEL_ID,
    device=DEVICE,
    trust_remote_code=True
)


class EmbeddingsRequest(BaseModel):
    model: Optional[str] = None
    input: Any  # OpenAI allows string | array[str]


@app.get("/health")
def health():
    return {"status": "ok", "model_id": MODEL_ID, "device": DEVICE}


@app.get("/v1/models")
def list_models():
    # Minimal OpenAI format
    return {
        "object": "list",
        "data": [
            {
                "id": "vi-embed",
                "object": "model",
                "owned_by": "local",
            }
        ],
    }


@app.post("/v1/embeddings")
def embeddings(req: EmbeddingsRequest):
    # Normalize input to list[str]
    if isinstance(req.input, str):
        texts = [req.input]
    elif isinstance(req.input, list):
        texts = ["" if t is None else str(t) for t in req.input]
    else:
        texts = [str(req.input)]

    # IMPORTANT: Must return 1 embedding per input (avoid “expected N got M”)
    # Handle empty strings -> embed anyway (or return zeros)
    safe_texts = [t if t.strip() else " " for t in texts]

    vectors: List[List[float]] = []
    for i in range(0, len(safe_texts), MAX_BATCH):
        batch = safe_texts[i : i + MAX_BATCH]
        emb = model.encode(
            batch,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        emb = np.asarray(emb, dtype=np.float32)
        vectors.extend(emb.tolist())

    data = [{"object": "embedding", "index": i, "embedding": vec} for i, vec in enumerate(vectors)]
    return {
        "object": "list",
        "data": data,
        "model": req.model or "vi-embed",
        "usage": {"prompt_tokens": 0, "total_tokens": 0},
    }
