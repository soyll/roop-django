from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Review, FaceSwapTask
from .serializers import ReviewSerializer, FaceSwapTaskCreateSerializer, FaceSwapTaskStatusSerializer
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

class FaceSwapTaskStatusView(APIView):
    def get(self, request, pk):
        try:
            task = FaceSwapTask.objects.get(pk=pk)
        except FaceSwapTask.DoesNotExist:
            return Response({"detail": "Задача не найдена"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FaceSwapTaskStatusSerializer(task, context={'request': request})
        return Response(serializer.data)