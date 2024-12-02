
    
from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files import File


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    registered_time = models.DateTimeField(auto_now_add=True)
    qr_data = models.CharField(max_length=255, blank=True, null=True)  # 存储二维码数据

    def save(self, *args, **kwargs):
        if not self.qr_data:
            self.qr_data = f"{self.user.username}_profile"
        super().save(*args, **kwargs)
    def __str__(self):
        return self.user.username
