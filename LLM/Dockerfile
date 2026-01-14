FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MODEL_ID="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" \
    DEVICE="cpu"

WORKDIR /app

# deps hệ thống tối thiểu
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# copy code
COPY app.py /app/app.py

# preload model ở build-time để chạy phát ăn ngay (cần internet khi build)
RUN python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('${MODEL_ID}', device='cpu'); print('Model cached OK')"

EXPOSE 8888

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8888"]
