import csv
import os
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import FileResponse
from django.conf import settings
from django.utils.timezone import now
from django.core.files.storage import default_storage

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

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

@extend_schema(
    responses=FaceSwapTaskStatusSerializer
)
class FaceSwapTaskStatusView(APIView):
    def get(self, request, pk):
        try:
            task = FaceSwapTask.objects.get(pk=pk)
        except FaceSwapTask.DoesNotExist:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FaceSwapTaskStatusSerializer(task, context={'request': request})
        return Response(serializer.data)

@extend_schema(
    request=TemplateReplaceSerializer,
    responses={200: OpenApiResponse(description="Template replaced successfully")},
)
class TemplateReplaceView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request):
        serializer = TemplateReplaceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        template_type = serializer.validated_data['type']
        image_file = serializer.validated_data['image']

        try:
            img = Image.open(image_file)
            os.makedirs('/app/templates/', exist_ok=True)
            path = f'/app/templates/{template_type}.png'
            img.convert("RGB").save(path, format="PNG")
            return Response({'success': True})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
@extend_schema(
    parameters=[
        ReportDownloadSerializer().fields['password'],
    ],
    responses={200: OpenApiResponse(description="CSV file downloaded")}
)
class DownloadReportView(APIView):
    def get(self, request):
        serializer = ReportDownloadSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        password = serializer.validated_data['password']
        if password != settings.CSV_PASSWORD:
            return Response({'error': 'Incorrect password'}, status=403)

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

@extend_schema(
    request=ReportUploadSerializer,
    responses={200: OpenApiResponse(description="CSV file uploaded successfully")},
)
class UploadReportView(APIView):
    def post(self, request):
        serializer = ReportUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        file = serializer.validated_data['file']
        filename = f'report_upload_{now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        path = default_storage.save(f'reports/{filename}', file)

        return Response({'success': True, 'path': path})