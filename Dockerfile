FROM python:3.11-slim

WORKDIR /app

# OpenCV runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY scripts/ scripts/

# Download MediaPipe pose model at build time
RUN python scripts/download_model.py

RUN mkdir -p data/metrics

ENV POSE_MODEL_PATH=models/pose_landmarker_lite.task
ENV METRICS_DIR=data/metrics
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
