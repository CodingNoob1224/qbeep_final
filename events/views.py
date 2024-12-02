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
@staff_member_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', event_id=event.id)  # Make sure event_id is used here
    else:
        form = EventForm(instance=event)
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})

from django.utils import timezone
from .models import Event
from datetime import datetime

@login_required(login_url='login')
def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {
        'events': events,
        'now': now(),  # 傳遞當前時間給模板
    })
    # 取得活動類別和時間篩選條件
    activity_type = request.GET.get('activity_type')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    # 獲取所有活動並進行篩選
    events = Event.objects.all()

    if activity_type:
        events = events.filter(activity_type=activity_type)

    # if start_time:
    #     try:
    #         start_time = timezone.make_aware(datetime.strptime(start_time, '%Y-%m-%d %H:%M'))
    #         events = events.filter(event_time__gte=start_time)
    #     except ValueError:
    #         pass  # 當 start_time 不是有效的日期格式時不篩選

    # if end_time:
    #     try:
    #         end_time = timezone.make_aware(datetime.strptime(end_time, '%Y-%m-%d %H:%M'))
    #         events = events.filter(event_time__lte=end_time)
    #     except ValueError:
    #         pass  # 當 end_time 不是有效的日期格式時不篩選

    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = Registration.objects.filter(user=request.user, event=event).exists()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_registered': is_registered,
        'now': now()  
    })


@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if registration is open
    if not (event.registration_start <= now() <= event.registration_end):
        messages.error(request, '目前非報名時間，無法報名此活動。')
        return redirect('event_detail', event_id=event_id)

    # Check if event capacity is full
    current_registration_count = Registration.objects.filter(event=event).count()
    if current_registration_count >= event.capacity_limit:
        messages.error(request, '此活動名額已滿，無法報名。')
    else:
        # Check if user is already registered
        if not Registration.objects.filter(user=request.user, event=event).exists():
            Registration.objects.create(user=request.user, event=event)
            messages.success(request, '您已成功報名活動！')
        else:
            messages.warning(request, '您已經報名過此活動。')
    return redirect('event_detail', event_id=event_id)


@login_required
def cancel_registration(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    # Check if the user is registered for the event
    registration = Registration.objects.filter(user=request.user, event=event).first()
    if registration:
        registration.delete()
        messages.success(request, '您已成功取消報名！')
    else:
        messages.warning(request, '您尚未報名此活動。')
    return redirect('event_detail', event_id=event_id)


def create_event(request):
    error_messages = []
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')  # Redirect to the event list or another page
        else:
            # Collect error messages from the form
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


