FROM python:3.13-slim
WORKDIR /app
COPY worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY worker/worker.py .
COPY shared ./shared
ENV PYTHONPATH=/app
CMD ["python", "worker.py"]