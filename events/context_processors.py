# events/context_processors.py
from events.models import Event

def is_event_manager(request):
    if request.user.is_authenticated:
        return {
            'is_event_manager': Event.objects.filter(managers=request.user).exists()
        }
    return {'is_event_manager': False}
