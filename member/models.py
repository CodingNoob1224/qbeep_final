
    
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
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # 生成 QR 码并保存到 qr_code 字段
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f'{self.user.username}_profile')
            qr.make(fit=True)

            # 生成图像
            img = qr.make_image(fill='black', back_color='white')

            # 将图片保存到内存
            qr_image = BytesIO()
            img.save(qr_image, format='PNG')
            qr_image.seek(0)

            # 保存到模型字段
            self.qr_code.save(f'{self.user.username}_qr.png', File(qr_image), save=False)
        
        super().save(*args, **kwargs)
    def __str__(self):
        return self.user.username
