from rest_framework import serializers
from .models import Review, FaceSwapTask

class ReviewSerializer(serializers.ModelSerializer):
    task_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Review
        fields = ['id', 'session_id', 'task_id', 'text', 'rating', 'created_at']

    def validate_task_id(self, value):
        if not FaceSwapTask.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Task not found")
        if Review.objects.filter(task_id=value).exists():
            raise serializers.ValidationError("A review for this task already exists")
        return value

    def create(self, validated_data):
        task_id = validated_data.pop('task_id')
        task = FaceSwapTask.objects.get(pk=task_id)
        review = Review.objects.create(task=task, **validated_data)
        return review

class FaceSwapTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceSwapTask
        fields = ['id', 'user_photo', 'template_id', 'session_id']

class FaceSwapTaskStatusSerializer(serializers.ModelSerializer):
    user_photo = serializers.SerializerMethodField()
    result_photo = serializers.SerializerMethodField()

    class Meta:
        model = FaceSwapTask
        fields = ['id', 'status', 'user_photo', 'result_photo', 'error_message']

    def get_user_photo(self, obj):
        request = self.context.get('request')
        if obj.user_photo and hasattr(obj.user_photo, 'url'):
            return request.build_absolute_uri(obj.user_photo.url)
        return None

    def get_result_photo(self, obj):
        request = self.context.get('request')
        if obj.result_photo and hasattr(obj.result_photo, 'url'):
            return request.build_absolute_uri(obj.result_photo.url)
        return None