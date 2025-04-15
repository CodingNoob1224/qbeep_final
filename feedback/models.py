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
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    draw_time  = models.DateTimeField(auto_now_add=True)  # 記錄中獎時間

    class Meta:
        unique_together = None  # 移除 UNIQUE 限制

# feedback/models.py

from django.db import models
from django.contrib.auth.models import User
from events.models import Event
from .models import Registration  # 你之前的報名資料模型

class Question(models.Model):
    form = models.ForeignKey('Form', on_delete=models.CASCADE, related_name='questions')

    QUESTION_TYPES = [
        ('rating', '0-10 評分'),
        ('single_choice', '單選'),
        ('text', '文字回答'),
    ]
    content = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    options = models.TextField(blank=True, help_text='選項用逗號分隔，例如：極佳, 相當好, 良好')

    def get_options_list(self):
        return self.options.split(',') if self.options else []

    def __str__(self):
        return self.content[:50]
class Form(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Response(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    submit_time = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
