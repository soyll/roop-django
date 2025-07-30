import csv
import os

from django.forms import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import FileResponse
from django.conf import settings
from django.utils.timezone import now
from django.core.files.storage import default_storage

from .models import Review, FaceSwapTask
from .serializers import (
    ReportDownloadSerializer,
    ReportUploadSerializer,
    ReviewSerializer,
    FaceSwapTaskCreateSerializer,
    FaceSwapTaskStatusSerializer,
    TemplateReplaceSerializer
)
from .tasks import process_face_swap_task


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer


class FaceSwapTaskCreateView(generics.CreateAPIView):
    queryset = FaceSwapTask.objects.all()
    serializer_class = FaceSwapTaskCreateSerializer

    def perform_create(self, serializer):
        task = serializer.save(status='pending')
        process_face_swap_task.delay(str(task.id))
        return task
    
    def _format_error(self, exc):
        if isinstance(exc.detail, dict):
            for field, errors in exc.detail.items():
                if isinstance(errors, list) and errors:
                    return f"{field} {errors[0]}"
                return f"{field} {errors}"
        elif isinstance(exc.detail, list) and exc.detail:
            return str(exc.detail[0])
        return "Invalid input"

class FaceSwapTaskStatusView(APIView):
    def get(self, request, pk):
        try:
            task = FaceSwapTask.objects.get(pk=pk)
        except FaceSwapTask.DoesNotExist:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FaceSwapTaskStatusSerializer(task, context={'request': request})
        return Response(serializer.data)


class TemplateReplaceView(APIView):
    serializer_class = TemplateReplaceSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        template_type = serializer.validated_data['type']
        image_file = serializer.validated_data['image']

        try:
            img = Image.open(image_file)
            os.makedirs('media/templates/', exist_ok=True)
            path = f'media/templates/{template_type}.png'
            img.convert("RGB").save(path, format="PNG")
            return Response({'success': True})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DownloadReportView(APIView):
    serializer_class = ReportDownloadSerializer

    def get(self, request):
        serializer = self.serializer_class(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        password = serializer.validated_data['password']
        if password != settings.CSV_PASSWORD:
            return Response({'error': 'Incorrect password'}, status=status.HTTP_403_FORBIDDEN)

        filename = 'faceswap_report.csv'
        filepath = os.path.join(settings.MEDIA_ROOT, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Session ID', 'Status', 'Result', 'Error', 'Created', 'Updated'])
            for task in FaceSwapTask.objects.all():
                writer.writerow([
                    str(task.id),
                    task.session_id,
                    task.status,
                    task.result_photo.url if task.result_photo else '',
                    task.error_message,
                    task.created_at,
                    task.updated_at,
                ])

        return FileResponse(open(filepath, 'rb'), filename=filename, as_attachment=True)


class UploadReportView(APIView):
    serializer_class = ReportUploadSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']
        filename = f'faceswap_report_upload_{now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        path = default_storage.save(f'reports/{filename}', file)

        return Response({'success': True, 'path': path})
