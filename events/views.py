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

from django.utils.timezone import make_aware
from datetime import datetime
from events.models import Event
from django.shortcuts import render
from django.core.paginator import Paginator

def event_list(request):
    events = Event.objects.all().order_by('-published_time')  # ✅ 新到舊排序
    activity_type = request.GET.get('activity_type')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    # ✅ 篩選活動類別
    if activity_type:
        events = events.filter(activity_type=activity_type)

    # ✅ 篩選開始時間
    if start_time:
        try:
            start_dt = make_aware(datetime.fromisoformat(start_time))
            events = events.filter(event_time__gte=start_dt)
        except:
            pass

    # ✅ 篩選結束時間
    if end_time:
        try:
            end_dt = make_aware(datetime.fromisoformat(end_time))
            events = events.filter(event_time__lte=end_dt)
        except:
            pass

    # ✅ 分頁功能，每頁 10 筆
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events/event_list.html', {
        'events': page_obj,      # ✅ 傳遞分頁後的資料
        'now': now(),
        'page_obj': page_obj     # ✅ 傳遞分頁物件供 HTML 使用
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

from events.decorators import has_event_permission

@has_event_permission
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


@has_event_permission
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
from events.models import Event, Registration
from feedback.models import Response

from django.contrib.auth.decorators import login_required
from feedback.models import Form

from events.models import Event, Registration
from feedback.models import Form, Response
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def event_analysis(request):
    user = request.user

    if user.is_staff:
        events = Event.objects.all()
    else:
        events = Event.objects.filter(managers=user)

    event_data = []

    for event in events:
        registrations_count = Registration.objects.filter(event=event, status='registered').count()

        # ✅ 正確放在 for 迴圈裡面
        form = Form.objects.filter(event=event).first()
        if form:
            responses = Response.objects.filter(form=form)
            feedback_count = responses.count()

        event_data.append({
            'event': event,
            'registrations_count': registrations_count,
            'feedback_count': feedback_count,
        })

    return render(request, 'feedback/event_analysis.html', {
        'event_data': event_data
    })



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
@has_event_permission
def check_out_page(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/check_out_page.html', {'event': event})

import csv
import io
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from django.utils.timezone import localtime
from django.contrib.admin.views.decorators import staff_member_required
from .models import Event, Registration
from django.shortcuts import get_object_or_404

@has_event_permission
def export_registrations_csv(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registrations = Registration.objects.filter(event=event)

    # 使用 StringIO 暫存文字
    text_buffer = io.StringIO()
    writer = csv.writer(text_buffer)
    
    # 寫入欄位標題（中文）
    writer.writerow(['帳號', '姓名', '報名狀態', '報名時間', '簽到', '簽到時間', '簽退', '簽退時間'])

    # 寫入每筆報名資料
    for reg in registrations:
        writer.writerow([
            reg.user.username,
            reg.user.get_full_name() or reg.user.username,
            '已報名' if reg.status == 'registered' else '取消報名',
            "'" + localtime(reg.registration_time).strftime("%Y-%m-%d %H:%M"),
            '是' if reg.is_checked_in else '否',
            "'" + localtime(reg.check_in_time).strftime("%Y-%m-%d %H:%M") if reg.check_in_time else '',
            '是' if reg.is_checked_out else '否',
            "'" + localtime(reg.check_out_time).strftime("%Y-%m-%d %H:%M") if reg.check_out_time else '',
        ])

    # 編碼為 UTF-8 with BOM，讓 Excel 正確顯示中文
    content = '\ufeff' + text_buffer.getvalue()
    byte_buffer = content.encode('utf-8-sig')

    # 傳回 CSV 檔案
    filename = f"{event.name}_名單.csv"
    response = HttpResponse(byte_buffer, content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{escape_uri_path(filename)}'
    return response
import csv
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Event, Registration
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from .models import Event, Registration
from .utils import parse_usernames_from_csv  # 請確認有 utils.py
from events.decorators import has_event_permission

from django.shortcuts import render, redirect, get_object_or_404


@has_event_permission
def import_registrations_csv(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    messages = []

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        usernames, parse_errors = parse_usernames_from_csv(csv_file)

        for username in usernames:
            user = User.objects.filter(username=username).first()
            if not user:
                messages.append(f'❌ 帳號 {username} 不存在')
                continue

            if Registration.objects.filter(user=user, event=event).exists():
                messages.append(f'⚠️ {username} 已報名，略過')
                continue

            if event.event_registrations.count() >= event.capacity_limit:
                messages.append(f'⛔ 名額已滿，無法替 {username} 報名')
                continue

            Registration.objects.create(user=user, event=event)
            messages.append(f'✅ 成功報名：{username}')

        messages += parse_errors  # 將解析錯誤也顯示出來

    return render(request, 'events/import_registrations.html', {
        'event': event,
        'messages': messages
    })
