import os
from celery import shared_task

from faceswap.utils import run_faceswap, run_upscale
from .models import FaceSwapTask

from PIL import Image
from io import BytesIO

@shared_task
def process_face_swap_task(task_id, user_photo_bytes, template_id):
    task = FaceSwapTask.objects.get(pk=task_id)
    task.status = 'processing'
    task.save()

    try:
        user_photo_image = Image.open(BytesIO(user_photo_bytes))
        user_photo_image = user_photo_image.convert('RGB')

        user_photo_path = f'/tmp/{task_id}_user_photo.png'
        user_photo_image.save(user_photo_path, format='PNG')

        template_path = f"/app/templates/{template_id}.png"

        outdir = os.path.join('media', 'faceswap_results', str(task.id))
        os.makedirs(outdir, exist_ok=True)

        faceswap_result = run_faceswap(user_photo_path, template_path, outdir)
        if not faceswap_result:
            raise RuntimeError("No output from roop")

        upscaled_result = run_upscale(faceswap_result, outdir)

        with open(upscaled_result, 'rb') as f:
            task.result_photo.save(os.path.basename(upscaled_result), f, save=True)

        task.status = 'done'
        task.save()
    except Exception as e:
        task.status = 'error'
        task.error_message = str(e)
        task.save()
