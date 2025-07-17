import os
from celery import shared_task

from faceswap.utils import run_roop
from .models import FaceSwapTask

@shared_task
def process_face_swap_task(task_id):
    task = FaceSwapTask.objects.get(pk=task_id)
    task.status = 'processing'
    task.save()

    try:
        source = task.user_photo.path
        template = f"/app/templates/{task.template_id}.jpg"
        outdir = os.path.join('media', 'faceswap_results', str(task.id))
        os.makedirs(outdir, exist_ok=True)

        outputs = run_roop(source, template, outdir)
        if not outputs:
            raise RuntimeError("No output from roop")

        best = outputs[0]
        with open(best, 'rb') as f:
            task.result_photo.save(os.path.basename(best), f, save=True)

        task.status = 'done'
        task.save()
    except Exception as e:
        task.status = 'error'
        task.error_message = str(e)
        task.save()
