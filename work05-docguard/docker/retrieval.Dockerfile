FROM python:3.13-slim
WORKDIR /app
COPY python/retrieval/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY python/retrieval/main.py .
ENV CORPUS_DIR=/corpus
EXPOSE 8097
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8097"]