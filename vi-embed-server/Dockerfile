FROM python:3.11-slim

WORKDIR /app

# basic deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/app.py

ENV MODEL_ID=dangvantuan/vietnamese-document-embedding
ENV DEVICE=cpu
ENV MAX_BATCH=32

EXPOSE 8082
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8082"]
