import subprocess
from pathlib import Path
import os

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

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Roop failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")

    outputs = list(Path(output_path).glob("*"))
    return outputs
