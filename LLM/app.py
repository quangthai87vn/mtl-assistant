import os
import time
from typing import List, Union, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

APP_NAME = "MTL-LLM (Embedding Server)"

MODEL_ID = os.getenv("MODEL_ID", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
DEVICE = os.getenv("DEVICE", "cpu")  # cpu | cuda

app = FastAPI(title=APP_NAME)

model: Optional[SentenceTransformer] = None


class EmbeddingsRequest(BaseModel):
    model: Optional[str] = None
    input: Union[str, List[str]]
    normalize: bool = True  # normalize embeddings (cosine-friendly)


class EmbeddingItem(BaseModel):
    object: str = "embedding"
    index: int
    embedding: List[float]


class EmbeddingsResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingItem]
    model: str
    usage: dict


@app.on_event("startup")
def startup():
    global model
    mid = MODEL_ID
    model = SentenceTransformer(mid, device=DEVICE)


@app.get("/health")
def health():
    return {"ok": True, "model_id": MODEL_ID, "device": DEVICE}


@app.post("/v1/embeddings", response_model=EmbeddingsResponse)
def embeddings(req: EmbeddingsRequest):
    global model
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    mid = req.model or MODEL_ID

    # Nếu user gửi model khác với MODEL_ID thì hiện tại mình không hot-swap
    if mid != MODEL_ID:
        raise HTTPException(
            status_code=400,
            detail=f"Server is configured with MODEL_ID={MODEL_ID}. Received model={mid}.",
        )

    inputs = req.input if isinstance(req.input, list) else [req.input]

    t0 = time.time()
    vecs = model.encode(
        inputs,
        convert_to_numpy=True,
        normalize_embeddings=req.normalize,
        show_progress_bar=False,
    )
    dt = time.time() - t0

    vecs = np.asarray(vecs, dtype=np.float32)
    data = [
        EmbeddingItem(index=i, embedding=vecs[i].tolist())
        for i in range(vecs.shape[0])
    ]

    usage = {
        "input_count": len(inputs),
        "embedding_dim": int(vecs.shape[1]) if vecs.ndim == 2 else None,
        "compute_seconds": round(dt, 4),
    }

    return EmbeddingsResponse(data=data, model=MODEL_ID, usage=usage)
