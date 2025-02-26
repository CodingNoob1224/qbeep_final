from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    phone = models.CharField(unique = True, max_length=10, blank=True, null=True, default="N/A")
    birthday = models.DateField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True, default="未指定")
    registered_time = models.DateTimeField(auto_now_add=True)
    qr_data = models.CharField(max_length=255, blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  # 新增字段

    def save(self, *args, **kwargs):
        if not self.qr_data:
            self.qr_data = f"{self.user.username}_profile"
            print(f"QR Data set to: {self.qr_data}")  # 調試輸出
        
        # 生成 QR Code 圖片
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        file_name = f"user_{self.user.id}_qr.png"
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
        buffer.close()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.user

    # events/models.py
    from django.db import models
    from django.contrib.auth.models import User

    class Event(models.Model):
        name = models.CharField(max_length=200)
        event_time = models.DateTimeField()
        participants = models.ManyToManyField(
            User, related_name='member_checked_in_events'
        )
    def __str__(self):
        return self.user.username  # ✅ 應該返回 username，避免錯誤

