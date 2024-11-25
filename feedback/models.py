from django.db import models
from django.contrib.auth.models import User
from events.models import Event

# class Registration(models.Model):
#     STATUS_CHOICES = [
#         ('registered', '已報名'),
#         ('canceled', '取消報名'),
#     ]
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     registration_time = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)

#     def __str__(self):
#         return f"{self.user.username} - {self.event.name}"

# class Attendance(models.Model):
#     registration = models.OneToOneField(Registration, on_delete=models.CASCADE)
#     check_in_status = models.BooleanField(default=False)
#     check_in_time = models.DateTimeField(null=True, blank=True)
#     check_out_status = models.BooleanField(default=False)
#     check_out_time = models.DateTimeField(null=True, blank=True)
#     attended = models.BooleanField(default=False)

# class Question(models.Model):
#     QUESTION_TYPES = [
#         ('multiple_choice', '選擇題'),
#         ('fill_in_blank', '填空題'),
#     ]
    
#     question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)
#     question_content = models.TextField()
#     options = models.TextField(blank=True, null=True)  # 例如：用逗號分隔選項

# class Response(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
#     answer_content = models.TextField()
