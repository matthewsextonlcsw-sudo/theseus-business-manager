# Build from the repo root so the knowledge graph can be copied in:
#   docker build -f crm/connector/Dockerfile .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY crm/connector/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY crm/connector/connector ./connector
COPY knowledge/business-operating.grag.json ./knowledge/business-operating.grag.json

RUN useradd --system --uid 10001 connector && mkdir -p /data && chown connector /data
USER connector

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3).status == 200 else 1)"

# Only Caddy can reach this container, so trusting forwarded headers is safe here.
CMD ["uvicorn", "connector.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips", "*"]
