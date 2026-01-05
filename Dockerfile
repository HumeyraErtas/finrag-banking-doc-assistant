FROM python:3.11-slim

WORKDIR /app

# System deps (pdf + build tools minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

EXPOSE 8000

# Default: run API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
