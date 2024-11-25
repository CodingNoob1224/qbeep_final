from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Registration
from member.forms import EventForm


from django.contrib.admin.views.decorators import staff_member_required

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


@login_required(login_url='login')
def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    is_registered = Registration.objects.filter(user=request.user, event=event).exists()
    return render(request, 'events/event_detail.html', {'event': event})


# def event_detail(request, id):
#     event = get_object_or_404(Event, id=id)
#     # Check if the user is registered for the event
#     return render(request, 'events/event_detail.html', {'event': event, 'is_registered': is_registered})

@login_required
def register_event(request, id):
    event = get_object_or_404(Event, id=id)
    # Check if the event has reached its registration limit
    current_registration_count = Registration.objects.filter(event=event).count()
    if current_registration_count >= event.capacity_limit:
        messages.error(request, '此活動名額已滿，無法報名。')
    else:
        # Check if the user has already registered for this event
        if not Registration.objects.filter(user=request.user, event=event).exists():
            Registration.objects.create(user=request.user, event=event)
            messages.success(request, '您已成功報名活動！')
        else:
            messages.warning(request, '您已經報名過此活動。')
    return redirect('event_detail', id=id)

@login_required
def cancel_registration(request, id):
    event = get_object_or_404(Event, id=id)
    # Check if the user is registered for the event
    registration = Registration.objects.filter(user=request.user, event=event).first()
    if registration:
        registration.delete()
        messages.success(request, '您已成功取消報名！')
    else:
        messages.warning(request, '您尚未報名此活動。')
    return redirect('event_detail', id=id)

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

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Event

@staff_member_required
def check_in_page(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/check_in_page.html', {'event': event})

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import Event, Registration

@staff_member_required
def check_in_user(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        qr_code_data = request.POST.get('qr_code')
        registration = Registration.objects.filter(event=event, user__userprofile__qr_code=qr_code_data).first()
        if registration:
            registration.checked_in = True
            registration.save()
            return JsonResponse({'status': 'success', 'message': f'{registration.user.username} 簽到成功！'})
        else:
            return JsonResponse({'status': 'error', 'message': '無效的 QR 碼或用戶未註冊。'})
    return redirect('event_list')
