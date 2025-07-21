FROM python:3.11-bullseye

ARG INSTALL_ROOP=false

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git ffmpeg libgl1-mesa-glx libglib2.0-0 \
    build-essential cmake \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY /roop/requirements.txt /app/roop/requirements.txt
RUN pip install --no-cache-dir -r /app/roop/requirements.txt

COPY . .

CMD ["celery", "-A", "ar_tobolsk", "worker", "-l", "info", "-E"]