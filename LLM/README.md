# MTL-LLM (Embedding Server)

## Build đứng ở ngoài thư mục Parent
docker build -t mtl-llm:latest -f LLM/Dockerfile LLM

## Run (CPU)
docker run --rm -p 8888:8888 --name mtl-llm  \
  -e MODEL_ID="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" \
  -e DEVICE="cpu" \
  mtl-llm:latest

## Test
curl -s http://localhost:8888/health

curl -s http://localhost:8888/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input":"xin chào"}' | head
