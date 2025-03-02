# feedback/views.py
from django.shortcuts import get_object_or_404, render
from events.models import Event, Registration
from feedback.models import Check

def check_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registrations = Registration.objects.filter(event=event, status='registered')

    checks = []
    for registration in registrations:
        check, created = Check.objects.get_or_create(user=registration.user, event=event, registration=registration)
        checks.append({
            'user': registration.user,
            'is_checked_in': registration.is_checked_in,
            'check_in_time': registration.check_in_time if registration.is_checked_in else None,
            'check_out_time': registration.check_out_time if registration.is_checked_out else None
        })

    return render(request, 'feedback/check_detail.html', {
        'event': event,
        'checks': checks,
    })


from django.db.models import Count
from django.shortcuts import render
from events.models import Event
from feedback.models import Feedback

def event_analysis(request):
    events = Event.objects.annotate(
        registrations_count=Count('event_registrations')  # 聚合報名人數
    )
    event_data = []

    for event in events:
        feedback_count = event.feedback_set.count()  # 獲取回饋數量
        event_data.append({
            'event': event,
            'registrations_count': event.registrations_count,  # 使用已計算的報名人數
            'feedback_count': feedback_count,
        })

    return render(request, 'feedback/event_analysis.html', {'event_data': event_data})

import random
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Winner
from events.models import Event
from feedback.models import Registration
from django.contrib.auth.decorators import user_passes_test

# 限制只有管理員才能抽獎
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import random
from events.models import Event
from feedback.models import Winner, Registration
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_staff

# 讓管理員選擇活動
@user_passes_test(is_admin)
def draw_home(request):
    events = Event.objects.all()
    return render(request, 'draw_home.html', {'events': events})

# 執行抽獎
@user_passes_test(is_admin)
def draw_winners(request, event_id):
    if request.method == "POST":
        event = get_object_or_404(Event, id=event_id)
        num_winners = int(request.POST.get("num_winners", 1))

        checked_in_users = Attendance.objects.filter(
            registration__event=event,
            check_in_status=True,
            check_out_status=False
        ).values_list("registration__user", "registration__user__username", "registration__user__email")

        existing_winners = Winner.objects.filter(event=event).values_list("user", flat=True)
        eligible_users = [user for user in checked_in_users if user[0] not in existing_winners]

        if len(eligible_users) < num_winners:
            return JsonResponse({"error": "可抽獎人數不足"}, status=400)

        selected_winners = random.sample(eligible_users, num_winners)

        # 存入資料庫
        winner_list = []
        for user in selected_winners:
            Winner.objects.create(event=event, user_id=user[0])
            winner_list.append({"name": user[1], "email": user[2]})

        return JsonResponse({"message": "抽獎完成", "winners": winner_list})

    return JsonResponse({"error": "僅支援 POST 請求"}, status=405)
