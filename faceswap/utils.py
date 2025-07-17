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

ROOP_PATH = "/app/roop/run.py"

def run_roop(source_path: str, target_path: str, output_path: str):
    os.makedirs(output_path, exist_ok=True)

    cmd = [
        "python", ROOP_PATH,
        "-s", source_path,
        "-t", target_path,
        "-o", output_path,
        "--frame-processor", "face_swapper"
    ]

    logging.info(f"Запускаю roop командой: {' '.join(cmd)}")

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
        for line in proc.stdout:
            logging.info(f"[ROOP] {line.strip()}")

        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"Roop завершился с ошибкой (код {proc.returncode})")

    outputs = list(Path(output_path).glob("*"))
    logging.info(f"Результаты в: {output_path}, файлов: {len(outputs)}")
    return outputs
