FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY config config
COPY src src
ENV PYTHONPATH=/app/src
EXPOSE 8098
CMD ["uvicorn", "work06.app_main:app", "--host", "0.0.0.0", "--port", "8098"]