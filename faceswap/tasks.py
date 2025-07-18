import os
from celery import shared_task
from faceswap.utils import run_roop, run_upscale
from .models import FaceSwapTask

@shared_task
def process_face_swap_task(task_id):
    task = FaceSwapTask.objects.get(pk=task_id)
    task.status = 'processing'
    task.save()

    try:
        source = task.user_photo.path
        template = f"/app/templates/{task.template_id}.png"
        outdir = os.path.join('media', 'faceswap_results')
        os.makedirs(outdir, exist_ok=True)
        outfile = os.path.join(outdir, f"{task.id}.png")

        run_roop(source, template, outfile)

        if not os.path.exists(outfile):
            raise RuntimeError(f"Roop не создал файл: {outfile}")
        
        run_upscale(outfile, outfile)

        with open(outfile, 'rb') as f:
            task.result_photo.save(os.path.basename(outfile), f, save=True)

        task.status = 'done'
        task.save()

    except Exception as e:
        task.status = 'error'
        task.error_message = str(e)
        task.save()
