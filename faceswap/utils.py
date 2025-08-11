import subprocess
import os
from pathlib import Path
import logging
import sys
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

ROOP_SCRIPT = "/app/roop/run.py"
UPSCALE_SCRIPT = "/app/gfpgan/inference_gfpgan.py"

def run_faceswap(source_path: str, target_path: str, output_path: str) -> str:
    logging.info(f"[ROOP] Running face swap task")
    
    os.makedirs(output_path, exist_ok=True)
    
    cmd = [
        "python3", ROOP_SCRIPT,
        "-s", source_path,
        "-t", target_path,
        "-o", output_path,
        "--execution-provider", "cuda",
        "--frame-processor", "face_swapper"
    ]
    logging.info(f"[ROOP] Running: {' '.join(cmd)}")
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
        for line in proc.stdout:
            logging.info(f"[ROOP] {line.strip()}")
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"[ROOP] [ERROR] Code: {proc.returncode}")

    outputs = [p for p in Path(output_path).iterdir() if p.is_file()]
    if not outputs:
        raise RuntimeError("[UPSCALE] Нет файлов в выходной папке")
    for f in outputs:
        if f.name.lower().endswith((".jpg", ".png")):
            return str(f)
    raise RuntimeError(f"[UPSCALE] В папке нет итогового изображения: {output_path}")

def run_upscale(input_image: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        "python3", UPSCALE_SCRIPT,
        "-i", input_image,
        "-o", output_dir,
        "-v", "1.3",
        "-s", "2",
        "--ext", "png"
    ]
    
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
        for line in proc.stdout:
            logging.info(f"[UPSCALE] {line.strip()}")
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"Upscale failed with code {proc.returncode}")

    upscaled_path = os.path.join(output_dir, 'restored_imgs', os.path.basename(input_image))
    with Image.open(upscaled_path) as img:
        img.resize((2048, 2048), Image.LANCZOS).save(upscaled_path, "PNG")
    
    return upscaled_path