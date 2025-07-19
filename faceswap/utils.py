import subprocess
import os
import logging
import sys
from super_image import PanModel, ImageLoader
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

ROOP_PATH = "/app/roop/run.py"

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
    image = Image.open(input_path)
    model = PanModel.from_pretrained('eugenesiow/pan', scale=2)
    inputs = ImageLoader.load_image(image)
    preds = model(inputs)
    ImageLoader.save_image(preds, output_path)
    logging.info(f"[UPSCALE] Enhanced image saved to {output_path}")