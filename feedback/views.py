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

