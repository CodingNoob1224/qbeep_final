from django.shortcuts import get_object_or_404
from .models import Event
from django.http import HttpResponseForbidden

def has_event_permission(view_func):
    """
    允許活動負責人或後台管理員操作該活動
    """
    def _wrapped_view(request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, id=event_id)
        user = request.user

        if user.is_staff or user in event.managers.all():
            return view_func(request, event_id, *args, **kwargs)

        return HttpResponseForbidden("您沒有權限管理此活動。")
    return _wrapped_view

