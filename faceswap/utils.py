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

def run_faceswap(source_path: str, target_path: str, output_path: str):
    os.makedirs(output_path, exist_ok=True)

    cmd = [
        "python", ROOP_SCRIPT   ,
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

    outputs = list(Path(output_path).glob("*"))
    logging.info(f"[ROOP] Results in directory: {output_path}, files: {len(outputs)}")
    return outputs

def run_upscale(input_image: str, output_dir: str):
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

    outputs = list(Path(output_dir).glob("*"))
    logging.info(f"[UPSCALE] Results in directory: {output_dir}, files: {len(outputs)}")
    return outputs