FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3.11 python3.11-dev python3.11-venv python3-pip \
    git ffmpeg libgl1-mesa-glx libglib2.0-0 \
    build-essential cmake \
    && ln -sf python3.11 /usr/bin/python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY roop/requirements.txt roop/requirements.txt

RUN pip install --no-cache-dir -r roop/requirements.txt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "ar_tobolsk", "worker", "-l", "info", "-E"]
