from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class Event(models.Model):
    ACTIVITY_TYPES = [
        ('lecture', '講座'),
        ('seminar', '研討會'),
    ]
    
    STATUS_CHOICES = [
        ('open', '報名中'),
        ('closed', '報名截止'),
        ('not_open', '尚未開放報名'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    event_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    capacity_limit = models.PositiveIntegerField()
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_open')

    published_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.name

    def clean(self):
        now = timezone.now()

        if self.published_time and self.event_time:
            if self.published_time >= self.event_time - timedelta(days=1):
                raise ValidationError("The event must be published at least one day before the event date.")

        if self.registration_start and self.registration_end:
            if self.registration_start >= self.registration_end:
                raise ValidationError("Registration start time must be earlier than the end time.")
            if self.registration_start <= now or self.registration_end <= now:
                raise ValidationError("Registration start and end times must be in the future.")

        if self.event_time and self.event_time <= now:
            raise ValidationError("The event date must be in the future.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Calls the clean() method to enforce validation
        super().save(*args, **kwargs)


class Registration(models.Model):
    STATUS_CHOICES = [
        ('registered', '已報名'),
        ('canceled', '取消報名'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(Event, related_name='event_registrations', on_delete=models.CASCADE)
    registration_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    is_checked_in = models.BooleanField(default=False)  # 確保這個欄位存在
    check_in_time = models.DateTimeField(null=True, blank=True)  # 新增簽到時間欄位
    is_checked_out = models.BooleanField(default=False)  # **新增簽退狀態**
    check_out_time = models.DateTimeField(null=True, blank=True)  # **新增簽退時間**

    def __str__(self):
        return f'{self.user.username} - {self.event.name}'
