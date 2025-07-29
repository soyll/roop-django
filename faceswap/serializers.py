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
    user_photo = serializers.ImageField(required=False)

    class Meta:
        model = FaceSwapTask
        fields = ['id', 'user_photo', 'user_photo_base64', 'template_id', 'session_id']

    def validate(self, attrs):
        if not attrs.get('user_photo') and not attrs.get('user_photo_base64'):
            raise serializers.ValidationError("Either 'user_photo' or 'user_photo_base64' must be provided.")
        return super().validate(attrs)

    def create(self, validated_data):
        base64_data = validated_data.pop('user_photo_base64', None)
        if base64_data:
            if not isinstance(base64_data, str):
                raise serializers.ValidationError("Photo must be a base64 string")

            if ';base64,' in base64_data:
                _, imgstr = base64_data.split(';base64,', 1)
            else:
                imgstr = base64_data

            imgstr = imgstr.strip().replace('\n', '').replace('\r', '').replace(' ', '')

            try:
                decoded_img = base64.b64decode(imgstr + '=' * (-len(imgstr) % 4))
            except Exception:
                raise serializers.ValidationError("Image base64 decode error")

            ext = imghdr.what(None, h=decoded_img)
            if not ext:
                raise serializers.ValidationError("Could not determine image type")

            file_name = f'{uuid.uuid4()}.{ext}'
            validated_data['user_photo'] = ContentFile(decoded_img, name=file_name)

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
    
class TemplateReplaceSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['male', 'female'])
    image = serializers.ImageField()
    
class ReportDownloadSerializer(serializers.Serializer):
    password = serializers.CharField()    

class ReportUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
