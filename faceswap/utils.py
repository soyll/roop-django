import os
import sys
import logging
import subprocess

from PIL import Image
import numpy as np
import cv2
from super_image import PanModel, ImageLoader
import insightface

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

ROOP_PATH = "/app/roop/run.py"

UPSCALE_MODEL = PanModel.from_pretrained('eugenesiow/pan', scale=2)

face_analyser = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
face_analyser.prepare(ctx_id=0)

def run_roop(source_path: str, target_path: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "python", ROOP_PATH,
        "-s", source_path,
        "-t", target_path,
        "-o", output_path,
        "--frame-processor", "face_swapper"
    ]

    logging.info(f"[ROOP] Starting roop with command: {' '.join(cmd)}")

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
        for line in proc.stdout:
            logging.info(f"[ROOP] {line.strip()}")
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"[ROOP] Exit with error code {proc.returncode}")

def run_upscale(input_path: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image_pil = Image.open(input_path).convert('RGB')
    image_np = np.array(image_pil)

    faces = face_analyser.get(image_np)
    if not faces:
        logging.warning("[UPSCALE] Лиц не найдено, сохраняю как есть.")
        image_pil.save(output_path)
        return

    result_np = image_np.copy()
    h, w, _ = image_np.shape

    for face in faces:
        x1, y1, x2, y2 = [int(v) for v in face['bbox']]

        pad = 10
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(w, x2 + pad)
        y2 = min(h, y2 + pad)

        face_crop = result_np[y1:y2, x1:x2, :]
        face_pil = Image.fromarray(face_crop)

        inputs = ImageLoader.load_image(face_pil)
        preds = UPSCALE_MODEL(inputs)
        upscaled_face = ImageLoader.get_image(preds)

        upscaled_np = np.array(upscaled_face)
        upscaled_np_resized = cv2.resize(upscaled_np, (x2-x1, y2-y1), interpolation=cv2.INTER_CUBIC)

        result_np[y1:y2, x1:x2, :] = upscaled_np_resized
        logging.info(f"[UPSCALE] Лицо {x1},{y1},{x2},{y2} апскейлено")

    Image.fromarray(result_np).save(output_path)
    logging.info(f"[UPSCALE] Enhanced image saved to {output_path}")
