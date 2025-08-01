import os
from celery import shared_task

from faceswap.utils import run_faceswap, run_upscale
from .models import FaceSwapTask

@shared_task(
    max_retries=3,
    soft_time_limit=180,
    time_limit=240,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True
)
def process_face_swap_task(task_id):
    task = FaceSwapTask.objects.get(pk=task_id)
    task.status = 'processing'
    task.save()

    try:
        source = task.user_photo.path
        template = os.path.join('media', 'templates', f"{task.template_id}.png")
        outdir = os.path.join('media', 'faceswap_results', str(task.id))
        os.makedirs(outdir, exist_ok=True)

        faceswap_result = run_faceswap(source, template, outdir)
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