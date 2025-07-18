FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git ffmpeg libgl1-mesa-glx libglib2.0-0 \
    build-essential cmake \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "ar_tobolsk.wsgi:application", "--bind", "0.0.0.0:8000"]
