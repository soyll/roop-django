import uuid
from django.db import models

class Review(models.Model):
    RATING_CHOICES = [
        ('5', '5'),
        ('4', '4'),
        ('3', '3'),
        ('2', '2'),
        ('1', '1'),
    ]
    
    task_id = models.OneToOneField('FaceSwapTask', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    rating = models.CharField(max_length=1, choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
class FaceSwapTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('processing', 'В процессе'),
        ('done', 'Готово'),
        ('error', 'Ошибка'),
    ]

    TEMPLATE_CHOICES = [
        ('male', 'Мужской шаблон'),
        ('female', 'Женский шаблон'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100)
    user_photo = models.ImageField(upload_to='uploads/user_photos/')
    template_id = models.CharField(max_length=10, choices=TEMPLATE_CHOICES)
    result_photo = models.ImageField(upload_to='uploads/result_photos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)