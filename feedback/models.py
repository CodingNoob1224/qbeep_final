# feedback/models.py
from django.db import models
from django.contrib.auth.models import User
from events.models import Event  # 引用 event 應用中的 Event 模型

class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_text = models.TextField()

    def __str__(self):
        return f'Feedback from {self.user.username} for {self.event.name}'
class FeedbackEvent(Event):  # 繼承自 Event 模型
    feedback_count = models.IntegerField(default=0)  # 例如：新增一個表示活動回饋數量的字段

    def __str__(self):
        return f'Feedback-enabled Event: {self.name}'
    
# models.py
from django.db import models
from django.contrib.auth.models import User
from events.models import Registration

class Check(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 用戶外鍵
    event = models.ForeignKey(Event, on_delete=models.CASCADE)  # 活動外鍵
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, null=True)  # 設置為可為 null
    check_in_time = models.DateTimeField(null=True, blank=True)  # 新增簽到時間欄位
    check_out_time = models.DateTimeField(null=True, blank=True)  # 新增簽退時間欄位

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"

    @property
    def is_checked_in(self):
        registration = Registration.objects.filter(user=self.user, event=self.event).first()
        return registration.is_checked_in if registration else False
    def is_checked_out(self):
        registration = Registration.objects.filter(user=self.user, event=self.event).first()
        return registration.is_checked_out if registration else False
from django.db import models
from django.contrib.auth import get_user_model
from events.models import Event  # 確保正確導入

User = get_user_model()

class Winner(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)  # 明確使用 Event 類別
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    draw_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
