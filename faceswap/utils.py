import subprocess
import os
from pathlib import Path
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

ROOP_SCRIPT = "/app/roop/run.py"
UPSCALE_SCRIPT = "/app/face-sparnet/test_enhance_single_unalign.py"
PRETRAIN_MODEL = "/app/face-sparnet/models/SPARNetHD_V4_Attn2D_net_H-epoch10.pth"

def run_faceswap(source_path: str, target_path: str, output_path: str) -> str:
    logging.info(f"[ROOP] Running face swap task")
    logging.info(f"[ROOP] Source path exists: {os.path.exists(source_path)} ({source_path})")
    logging.info(f"[ROOP] Target path exists: {os.path.exists(target_path)} ({target_path})")
    
    os.makedirs(output_path, exist_ok=True)
    
    cmd = [
        "python", ROOP_SCRIPT,
        "-s", source_path,
        "-t", target_path,
        "-o", output_path,
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
        "python", UPSCALE_SCRIPT,
        "--model", "sparnethd",
        "--name", "SPARNetHD_V4_Attn2D",
        "--res_depth", "10",
        "--att_name", "spar",
        "--Gnorm", "in",
        "--pretrain_model_path", PRETRAIN_MODEL,
        "--test_img_path", input_image,
        "--results_dir", output_dir
    ]
    logging.info(f"[UPSCALE] Running: {' '.join(cmd)}")
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
        for line in proc.stdout:
            logging.info(f"[UPSCALE] {line.strip()}")
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"[UPSCALE] [ERROR] Code: {proc.returncode}")

    for ext in (".jpg", ".png"):
        file_path = Path(output_dir) / f"hq_final{ext}"
        if file_path.exists():
            return str(file_path)

    raise RuntimeError(f"[UPSCALE] Image hq_final not found: {output_dir}")