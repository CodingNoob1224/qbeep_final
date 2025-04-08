from datetime import timedelta
from django import forms
from django.utils import timezone
from events.models import Event  # Make sure you are importing from the correct path
from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

# 忘記密碼驗證表單
class PasswordResetByPhoneForm(forms.Form):
    username = forms.CharField(label="使用者名稱", max_length=150)
    phone = forms.CharField(label="手機號碼", max_length=10)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        phone = cleaned_data.get("phone")

        # 確保 `UserProfile` 中有匹配的資料
        if not UserProfile.objects.filter(user__username=username, phone=phone).exists():
            raise forms.ValidationError("使用者名稱或手機號碼不正確，請重新輸入")

        return cleaned_data


# 新密碼設定表單
class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(label="新密碼", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="確認新密碼", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("兩次輸入的密碼不一致")

        return cleaned_data

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name', 'description', 'event_time', 'end_time', 'location', 'capacity_limit',
            'registration_start', 'registration_end', 'activity_type', 'status', 
            'poster', 'language'
        ]
    
    event_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    registration_start = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    registration_end = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    def clean(self):
        cleaned_data = super().clean()
        event_time = cleaned_data.get("event_time")
        registration_start = cleaned_data.get("registration_start")
        registration_end = cleaned_data.get("registration_end")
        
        now = timezone.now()

        # Validate registration times
        if registration_start and registration_end:
            if registration_start >= registration_end:
                self.add_error("registration_start", "開始報名時間要在截止時間之前")
            if registration_start <= now or registration_end <= now:
                self.add_error("registration_start", "開始報名時間要在未來")
                self.add_error("registration_end", "截止報名時間要在未來")

        # Ensure event time is also in the future if needed
        if event_time and event_time <= now:
            self.add_error("event_time", "活動時間要在未來")
        
        return cleaned_data
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="電子郵件")
    phone = forms.CharField(max_length=10, required=True, label="手機號碼")
    username = forms.CharField(max_length=150, required=True, label="姓名")

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        
            # 確保 `UserProfile` 被正確創建，並儲存 phone
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data["phone"]  # 儲存 phone 到 UserProfile
            profile.save()

        return user
# member/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileEditForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label='使用者名稱')
    email = forms.EmailField(required=True, label='信箱')

    class Meta:
        model = UserProfile
        fields = ['phone']  # 只編輯 profile 自己的欄位

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.user = user

    def save(self, commit=True):
        profile = super().save(commit=False)
        if hasattr(self, 'user'):
            self.user.username = self.cleaned_data['username']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile