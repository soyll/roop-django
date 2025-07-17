from rest_framework import serializers
from .models import Review, FaceSwapTask

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'session_id', 'text', 'rating', 'created_at']

class FaceSwapTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceSwapTask
        fields = ['id', 'user_photo', 'template_id', 'session_id']

class FaceSwapTaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceSwapTask
        fields = ['id', 'status', 'result_photo', 'error_message']
