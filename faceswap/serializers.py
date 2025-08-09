import base64
from PIL import Image
from io import BytesIO
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import Review, FaceSwapTask

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'task_id', 'text', 'rating', 'created_at']

class FaceSwapTaskCreateSerializer(serializers.ModelSerializer):
    user_photo_base64 = serializers.CharField(write_only=True, required=False)
    user_photo = serializers.ImageField(required=False)

    class Meta:
        model = FaceSwapTask
        fields = ['id', 'user_photo', 'user_photo_base64', 'template_id', 'session_id']

    def validate(self, data):
        if not data.get('user_photo') and not data.get('user_photo_base64'):
            raise serializers.ValidationError("Either 'user_photo' or 'user_photo_base64' must be provided.")
        return data

    def create(self, validated_data):
        base64_data = validated_data.pop('user_photo_base64', None)
        
        if base64_data:
            if ';base64,' in base64_data:
                _, base64_str = base64_data.split(';base64,', 1)
            else:
                base64_str = base64_data
            
            base64_str = base64_str.strip()
            
            try:
                decoded_img = base64.b64decode(base64_str + '=' * (-len(base64_str) % 4))
                img = Image.open(BytesIO(decoded_img))
                img_io = BytesIO()
                img.save(img_io, format='PNG')
                validated_data['user_photo'] = ContentFile(img_io.getvalue(), name=f"{validated_data.get('id')}.png")
            except Exception as e:
                raise serializers.ValidationError(f"Invalid image: {str(e)}")

        return super().create(validated_data)

class FaceSwapTaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceSwapTask
        fields = ['id', 'status', 'result_photo', 'error_message']

    def get_result_photo(self, obj):
        if obj.result_photo and hasattr(obj.result_photo, 'url'):
            return f"https://tobolsk.naviar.io{obj.result_photo.url}"
        return None
    
class TemplateReplaceSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['male', 'female'])
    image = serializers.ImageField()
    
class ReportDownloadSerializer(serializers.Serializer):
    password = serializers.CharField()    

class ReportUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
