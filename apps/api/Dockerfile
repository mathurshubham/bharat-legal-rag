FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

# Install deps first (cached layer — only invalidates when pyproject.toml changes)
COPY pyproject.toml .
RUN uv pip install --system --no-cache -e .

COPY app/ ./app/

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
