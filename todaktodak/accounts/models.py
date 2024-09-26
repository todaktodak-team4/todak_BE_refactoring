from django.contrib.auth.models import AbstractUser
from django.db import models
import os

def profile_image_upload_to(instance, filename):
    # 사용자 ID에 기반하여 파일 경로를 생성합니다.
    user_id = instance.id  # 또는 instance.pk
    base_filename, file_extension = os.path.splitext(filename)
    # 유효한 파일 이름을 생성합니다.
    filename = f"{base_filename}{file_extension}"
    return f'user_{user_id}/profiles/{filename}'

# Create your models here.
class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=10)
    profile = models.ImageField(upload_to=profile_image_upload_to, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True)
    postal_address = models.CharField(max_length=128, null=True)
    zone_code = models.CharField(max_length=128, null=True)
    address = models.CharField(max_length=128, null=True)
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.username