from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from events.models import Registration, Event
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.dispatch import receiver

from member.forms import EventForm
from .models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        return reverse_lazy('event_list')
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegistrationForm

# def register(request):
#     if request.method == "POST":
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)  # 註冊後自動登入
#             return redirect("event_list")  # 註冊成功後跳轉到活動列表
#     else:
#         form = UserRegistrationForm()

#     return render(request, "registration/register.html", {"form": form})

# def register(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             # 儲存用戶並創建 UserProfile
#             form.save()
#             return redirect('event_list')
#     else:
#         form = UserRegistrationForm()

#     return render(request, 'registration/register.html', {'form': form})
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ✅ 自動登入
            messages.success(request, "註冊成功，您已自動登入")
            return redirect('event_list')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})
import base64

@login_required
def profile(request):
    user = request.user
    registrations = Registration.objects.filter(user=user).select_related('event')

    # 確保 UserProfile 存在
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = None

    qr_code_base64 = None

    if profile and profile.qr_code:
        try:
            with profile.qr_code.open('rb') as f:
                qr_code_data = f.read()
                qr_code_base64 = base64.b64encode(qr_code_data).decode('utf-8')
        except Exception as e:
            print("讀 QR code 失敗：", e)

    return render(request, 'member/profile.html', {
        'user': user,
        'registrations': registrations,
        'qr_code_base64': qr_code_base64,  # ✅ 傳 base64 給前端
    })

# 管理员仪表板视图
@login_required
def admin_dashboard(request):
    events = Event.objects.all()  # 获取所有事件
    registrations = Registration.objects.all()  # 获取所有注册
    return render(request, 'member/admin_dashboard.html', {
        'events': events,
        'registrations': registrations
    })

# 创建事件视图
@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')  # 创建事件后跳转到管理员仪表板
    else:
        form = EventForm()
    return render(request, 'member/create_event.html', {'form': form})

# 信号处理器：自动创建 UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

# member/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# 修正模型導入
from events.models import Event  # 移至正確的應用
from .models import UserProfile

@csrf_exempt
def check_in_user(request, event_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            scanned_qr_data = data.get("qr_code")
            
            # 查找用戶和活動
            user_profile = UserProfile.objects.filter(qr_data=scanned_qr_data).first()
            event = Event.objects.filter(id=event_id).first()

            if not event:
                return JsonResponse({"success": False, "message": "活動不存在"})

            if not user_profile:
                return JsonResponse({"success": False, "message": "用戶未註冊"})

            user = user_profile.user

            # 檢查是否已簽到
            if event.participants.filter(id=user.id).exists():
                return JsonResponse({"success": False, "message": f"{user.username} 已簽到"})

            # 執行簽到
            event.participants.add(user)
            return JsonResponse({"success": True, "message": f"{user.username} 簽到成功"})

        except Exception as e:
            print("後端錯誤:", e)
            return JsonResponse({"success": False, "message": "發生錯誤，請稍後再試"})

    return JsonResponse({"success": False, "message": "僅接受 POST 請求"})
#from django.shortcuts import render, redirect
#from django.contrib.auth import login
#from .forms import UserRegistrationForm
#def register(request):
#    if request.method == "POST":
#        form = UserRegistrationForm(request.POST)
#        if form.is_valid():
#            user = form.save()
#            login(request, user)  # 註冊後自動登入
#            return redirect("event_list")  # 成功後跳轉到活動列表
#    else:
#        form = UserRegistrationForm()

# from django.contrib.auth import login
# from django.contrib import messages

# def register(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             print("註冊成功的使用者：", user)
#             login(request, user)  # ✅ 自動登入
#             messages.success(request, "註冊成功，您已自動登入")
#             return redirect("event_list")
#     else:
#         form = UserRegistrationForm()

#     return render(request, "registration/register.html", {"form": form})

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from .forms import PasswordResetByPhoneForm, SetNewPasswordForm
from .models import UserProfile

User = get_user_model()
def password_reset_by_phone(request):
    if request.method == "POST":
        form = PasswordResetByPhoneForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            phone = form.cleaned_data["phone"]
            user_profile = UserProfile.objects.get(user__username=username, phone=phone)

            # 記錄 user id 在 session 中，供下一步設定密碼使用
            request.session["reset_user_id"] = user_profile.user.id
            return redirect("set_new_password")
    else:
        form = PasswordResetByPhoneForm()

    return render(request, "registration/password_reset_by_phone.html", {"form": form})


def set_new_password(request):
    if "reset_user_id" not in request.session:
        messages.error(request, "未授權的請求")
        return redirect("password_reset_by_phone")

    user = User.objects.get(id=request.session["reset_user_id"])

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password"])
            user.save()

            # 自動登入並清除 session
            login(request, user)
            # del request.session["reset_user_id"]
            request.session.pop("reset_user_id", None)

            messages.success(request, "密碼已成功重設，您已自動登入")
            return redirect("event_list")  # 你可以換成首頁的路由名稱
    else:
        form = SetNewPasswordForm()

    return render(request, "registration/set_new_password.html", {"form": form})

from .forms import UserProfileEditForm

@login_required
def edit_profile(request):
    profile = request.user.userprofile

    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # 換成你個人頁的路由名稱
    else:
        form = UserProfileEditForm(instance=profile, user=request.user)

    return render(request, 'member/edit_profile.html', {'form': form})