FROM python:3.11.9-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git ffmpeg libgl1-mesa-glx libglib2.0-0 \
    build-essential cmake \
    && rm -rf /var/lib/apt/lists/*

COPY roop/requirements.txt roop/requirements.txt
RUN pip install --no-cache-dir -r roop/requirements.txt

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "ar_tobolsk", "worker", "-l", "info", "-E"]