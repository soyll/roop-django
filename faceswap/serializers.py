import base64
import imghdr
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Review, FaceSwapTask

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'session_id', 'text', 'rating', 'created_at']

class FaceSwapTaskCreateSerializer(serializers.ModelSerializer):
    user_photo_base64 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = FaceSwapTask
        fields = ['id', 'user_photo', 'user_photo_base64', 'template_id', 'session_id']

    def create(self, validated_data):
        base64_data = validated_data.pop('user_photo_base64', None)
        if base64_data:
            format, imgstr = base64_data.split(';base64,')
            ext = imghdr.what(None, h=base64.b64decode(imgstr))
            if not ext:
                raise serializers.ValidationError("Invalid image")
            file_name = f'{uuid.uuid4()}.{ext}'
            validated_data['user_photo'] = ContentFile(base64.b64decode(imgstr), name=file_name)
        return super().create(validated_data)

class FaceSwapTaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceSwapTask
        fields = ['id', 'status', 'result_photo', 'error_message']

    def get_result_photo(self, obj):
        request = self.context.get('request')
        if obj.result_photo and hasattr(obj.result_photo, 'url'):
            return request.build_absolute_uri(obj.result_photo.url)
        return None