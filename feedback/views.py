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

    # 取得中獎名單
    winners = Winner.objects.filter(event=event)

    return render(request, 'feedback/check_detail.html', {
        'event': event,
        'checks': checks,
        'winners': winners  # 傳遞中獎者資料
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
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import random
from events.models import Event
from feedback.models import Winner, Registration
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def draw_home(request):
    events = Event.objects.all()
    return render(request, 'draw_home.html', {'events': events})

import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Event, Registration, Winner

def is_admin(user):
    return user.is_staff  # 確保只有管理員可以抽獎

@user_passes_test(is_admin)
def draw_winners(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        num_winners = int(request.POST.get("num_winners", 1))
        
        event = get_object_or_404(Event, id=event_id)
        
        # 取得所有簽到的使用者
        checked_in_users = Registration.objects.filter(
            event=event, status="registered"
        ).values_list("user_id", "user__username")

        # 取得所有已經中獎的使用者
        existing_winners = Winner.objects.filter(event=event).values_list("user_id", flat=True)

        # 只從未中獎的人裡面抽
        eligible_users = [user for user in checked_in_users if user[0] not in existing_winners]

        if len(eligible_users) < num_winners:
            return render(request, 'draw_detail.html', {
                "winners": [], "error": "可抽獎人數不足"
            })

        # 隨機選擇中獎者
        selected_winners = random.sample(eligible_users, num_winners)
        winners_list = []
        for user in selected_winners:
            Winner.objects.create(event=event, user_id=user[0])
            winners_list.append({"name": user[1]})

        return render(request, 'draw_detail.html', {"winners": winners_list})

    return redirect('draw_home')


# feedback/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Form, Question, Response, Answer
from events.models import Event
from feedback.models import Registration
from django.db.models import Avg
@login_required
def feedback_dashboard(request):
    registrations = Registration.objects.filter(
        user=request.user,
        status='registered',
        check_in_time__isnull=False  # ✅ 有簽到時間
    )
    return render(request, 'feedback/dashboard.html', {'registrations': registrations})
@login_required
def fill_form(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    registration = get_object_or_404(
        Registration,
        user=request.user,
        event=event,
        status='registered',
        check_in_time__isnull=False  # ✅ 有簽到時間
    )
    form = get_object_or_404(Form, event=event)
    questions = Question.objects.all()

    if Response.objects.filter(form=form, registration=registration).exists():
        return render(request, 'feedback/already_filled.html', {'event': event})

    if request.method == 'POST':
        response = Response.objects.create(form=form, registration=registration)
        for question in questions:
            answer = request.POST.get(f'q_{question.id}', '')
            Answer.objects.create(response=response, question=question, content=answer)
        return render(request, 'feedback/thank_you.html')

    return render(request, 'feedback/fill_form.html', {
        'event': event,
        'questions': questions,
    })

from collections import Counter
from django.db.models import Avg
from django.http import JsonResponse
import json

@user_passes_test(lambda u: u.is_staff)
def form_analysis(request, event_id):
    form = get_object_or_404(Form, event_id=event_id)
    questions = Question.objects.all()
    responses = Response.objects.filter(form=form)
    avg_score = Answer.objects.filter(
        question=questions[0],
        response__form=form
    ).aggregate(avg=Avg('content'))['avg']

    answers = {
        q: Answer.objects.filter(question=q, response__form=form)
        for q in questions
    }

    # 統計選項題的次數（Chart.js 用）
    chart_data = {}
    for q in questions:
        if q.question_type in ['rating', 'single_choice']:
            answer_list = [a.content for a in answers[q]]
            counter = Counter(answer_list)
            chart_data[q.id] = dict(counter)

    return render(request, 'feedback/form_analysis.html', {
        'form': form,
        'avg_score': avg_score,
        'questions': questions,
        'answers': answers,
        'responses': responses,
        'chart_data': json.dumps(chart_data),
    })
