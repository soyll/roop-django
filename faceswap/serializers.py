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

    def get_result_photo(self, obj):
        request = self.context.get('request')
        if obj.result_photo and hasattr(obj.result_photo, 'url'):
            return request.build_absolute_uri(obj.result_photo.url)
        return None