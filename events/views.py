from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from .models import Event, Registration
from member.forms import EventForm
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
import json

def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {
        'events': events,
        'now': now(),
    })


# def event_detail(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     # 計算已報名的參與者數量
#     participants_count = event.registration_set.count()  # 獲取報名數量

#     is_registered = event.registration_set.filter(user=request.user).exists()  # 檢查當前用戶是否已報名

#     return render(request, 'events/event_detail.html', {
#         'event': event,
#         'participants_count': participants_count,  # 傳遞報名數量到模板
#         'is_registered': is_registered,
#         'now': now(),  # 傳遞當前時間
#     })
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participants_count = event.event_registrations.count()  # 修正 related_name

    is_registered = event.event_registrations.filter(user=request.user).exists()

    return render(request, 'events/event_detail.html', {
        'event': event,
        'participants_count': participants_count,
        'is_registered': is_registered,
        'now': now(),
    })

# @login_required
# def register_event(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
    
#     if not (event.registration_start <= now() <= event.registration_end):
#         messages.error(request, '目前非報名時間，無法報名此活動。')
#         return redirect('event_detail', event_id=event_id)

#     current_registration_count = Registration.objects.filter(event=event).count()
#     if current_registration_count >= event.capacity_limit:
#         messages.error(request, '此活動名額已滿，無法報名。')
#     elif not Registration.objects.filter(user=request.user, event=event).exists():
#         Registration.objects.create(user=request.user, event=event)
#         messages.success(request, '您已成功報名活動！')
#     else:
#         messages.warning(request, '您已經報名過此活動。')

#     return redirect('event_detail', event_id=event_id)

@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # 確保目前在報名時間內
    if not (event.registration_start <= now() <= event.registration_end):
        messages.error(request, '目前非報名時間，無法報名此活動。')
        return redirect('event_detail', event_id=event_id)

    # 計算目前報名人數
    current_registration_count = event.event_registrations.count()

    # 確保報名人數未超過活動上限
    if current_registration_count >= event.capacity_limit:
        messages.error(request, '此活動名額已滿，無法報名。')
    elif not event.event_registrations.filter(user=request.user).exists():
        Registration.objects.create(user=request.user, event=event)
        messages.success(request, '您已成功報名活動！')
    else:
        messages.warning(request, '您已經報名過此活動。')

    return redirect('event_detail', event_id=event_id)

@login_required
def cancel_registration(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registration = Registration.objects.filter(user=request.user, event=event).first()
    if registration:
        registration.delete()
        messages.success(request, '您已成功取消報名！')
    else:
        messages.warning(request, '您尚未報名此活動。')
    return redirect('event_detail', event_id=event_id)


@staff_member_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@staff_member_required
def create_event(request):
    error_messages = []
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
    else:
        form = EventForm()
    return render(request, 'event/create_event.html', {'form': form, 'error_messages': error_messages})


@staff_member_required
def check_in_page(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/check_in_page.html', {'event': event})


@staff_member_required
def check_in_user(request, event_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        qr_code = data.get('qr_code')
        event = get_object_or_404(Event, id=event_id)

        registration = Registration.objects.filter(
            event=event, user__userprofile__qr_data=qr_code
        ).first()

        if registration:
            registration.checked_in = True
            registration.save()
            return JsonResponse({'success': True, 'message': f'{registration.user.username} 簽到成功！'})
        else:
            return JsonResponse({'success': False, 'message': '無效的 QR 碼或用戶未註冊。'})
    return JsonResponse({'success': False, 'message': '無效的請求。'})

from django.shortcuts import render
from events.models import Event  # 引用 events 应用中的 Event 模型
from feedback.models import Feedback  # 引用 feedback 应用中的 Feedback 模型

def event_analysis(request):
    events = Event.objects.all()  # 获取所有活动
    event_data = []

    for event in events:
        # 获取每个活动的报名用户数和反馈数量
        registrations_count = event.participants.count()  # 使用反向查询来计算报名数量
        feedback_count = event.feedbacks.count()  # 假设 Event 和 Feedback 有关联，并且是反向查询
        event_data.append({
            'event': event,
            'registrations_count': registrations_count,
            'feedback_count': feedback_count,
        })
    
    return render(request, 'feedback/event_analysis.html', {'event_data': event_data})

from django.shortcuts import render, get_object_or_404
from .models import Event

def check_in_page(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "events/check_in_page.html", {"event": event})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Event, Registration
from member.models import UserProfile  # 確保導入你的 Member 模型
import json
from django.utils.timezone import now  # 引入 now 方法

@csrf_exempt
def check_in_user(request, event_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            qr_code = data.get("qr_code")
            event = get_object_or_404(Event, id=event_id)

            print(f"收到的 QR Code: '{qr_code}'")

            user_profile = UserProfile.objects.filter(qr_data=qr_code).first()
            if not user_profile:
                return JsonResponse({"success": False, "message": "無效的 QR 碼。"})

            print(f"找到 UserProfile: {user_profile}, User: {user_profile.user}")

            registration = Registration.objects.filter(event=event, user=user_profile.user).first()
            if not registration:
                return JsonResponse({"success": False, "message": "用戶未報名此活動。"})

            print(f"找到的報名記錄: {registration}")

            # 更新簽到狀態與時間
            registration.is_checked_in = True
            registration.check_in_time = now()  # 記錄當前時間
            registration.save()

            return JsonResponse({
                "success": True,
                "message": f"{user_profile.user.username} 簽到成功！",
                "check_in_time": registration.check_in_time.strftime("%Y-%m-%d %H:%M:%S")
            })

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "無效的請求"})

@csrf_exempt
def check_out_user(request, event_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            qr_code = data.get("qr_code")
            event = get_object_or_404(Event, id=event_id)

            print(f"收到的 QR Code: '{qr_code}'")

            user_profile = UserProfile.objects.filter(qr_data=qr_code).first()
            if not user_profile:
                return JsonResponse({"success": False, "message": "無效的 QR 碼。"})

            print(f"找到 UserProfile: {user_profile}, User: {user_profile.user}")

            registration = Registration.objects.filter(event=event, user=user_profile.user).first()
            if not registration:
                return JsonResponse({"success": False, "message": "用戶未報名此活動。"})

            print(f"找到的報名記錄: {registration}")

            # 確保用戶已簽到但未簽退
            if not registration.is_checked_in:
                return JsonResponse({"success": False, "message": "用戶尚未簽到，無法簽退。"})

            if registration.is_checked_out:
                return JsonResponse({"success": False, "message": "用戶已簽退，無需重複操作。"})

            # 更新簽退狀態與時間
            registration.is_checked_out = True
            registration.check_out_time = now()  # 記錄當前時間
            registration.save()

            return JsonResponse({
                "success": True,
                "message": f"{user_profile.user.username} 簽退成功！",
                "check_out_time": registration.check_out_time.strftime("%Y-%m-%d %H:%M:%S")
            })

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "無效的請求"})
@staff_member_required
def check_out_page(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/check_out_page.html', {'event': event})