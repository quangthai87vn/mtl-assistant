from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import time

app = FastAPI()
model = SentenceTransformer("dangvantu an/vietnamese-document-embedding", device="mps")  # M2

class EmbReq(BaseModel):
    model: str | None = None
    input: str | list[str]

@app.get("/v1/models")
def models():
    return {"data": [{"id": "vi-doc-embed", "object": "model"}], "object": "list"}

@app.post("/v1/embeddings")
def embeddings(req: EmbReq):
    texts = req.input if isinstance(req.input, list) else [req.input]
    emb = model.encode(texts, normalize_embeddings=True)
    return {
        "object": "list",
        "data": [{"object": "embedding", "index": i, "embedding": emb[i].tolist()} for i in range(len(texts))],
        "model": "vi-doc-embed"
    }
