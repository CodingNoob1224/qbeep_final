# feedback/views.py
from django.shortcuts import get_object_or_404, render
from events.models import Event, Registration
from feedback.models import Check, Winner
from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
import random
from collections import Counter
import json
from django import forms
from .models import Question, Event  # Import your models
from django.forms import ModelForm 
from .forms import FeedbackForm
from feedback.models import Form
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Avg
from django.http import JsonResponse
import random, json
from collections import Counter

from feedback.models import (
    Check, Winner, Question, Form, Response, Answer
)
from events.models import Event, Registration
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

# def event_analysis(request):
#     user = request.user

#     if user.is_staff:
#         events = Event.objects.all()
#     else:
#         events = Event.objects.filter(managers=user)

#     event_data = []

#     for event in events:
#         registrations_count = Registration.objects.filter(event=event, status='registered').count()

#         # ✅ 正確放在 for 迴圈裡面
#         form = Form.objects.filter(event=event).first()
#         if form:
#             responses = Response.objects.filter(form=form)
#             feedback_count = responses.count()

#         event_data.append({
#             'event': event,
#             'registrations_count': registrations_count,
#             'feedback_count': feedback_count,
#         })

#     return render(request, 'feedback/event_analysis.html', {
#         'event_data': event_data
#     })

@login_required
def event_analysis(request):
    user = request.user

    # 管理員看到所有活動，負責人看到自己負責的活動
    if user.is_staff:
        events = Event.objects.all()
    else:
        events = Event.objects.filter(managers=user)

    event_data = []

    for event in events:
        registrations_count = Registration.objects.filter(event=event, status='registered').count()
        form = Form.objects.filter(event=event).first()
        feedback_count = Response.objects.filter(form=form).count() if form else 0

        event_data.append({
            'event': event,
            'registrations_count': registrations_count,
            'feedback_count': feedback_count,
        })

    return render(request, 'feedback/event_analysis.html', {
        'event_data': event_data
    })

# 抽獎管理員頁面
def is_admin(user):
    return user.is_staff

# @user_passes_test(is_admin)
# def draw_home(request):
#     events = Event.objects.all()
#     return render(request, 'draw_home.html', {'events': events})
from django.contrib.auth.decorators import login_required

@login_required
def draw_home(request):
    user = request.user

    if user.is_staff:
        events = Event.objects.all()
    else:
        events = Event.objects.filter(managers=user)

    return render(request, 'draw_home.html', {'events': events})

# @user_passes_test(is_admin)
# def draw_winners(request):
#     if request.method == "POST":
#         event_id = request.POST.get("event_id")
#         num_winners = int(request.POST.get("num_winners", 1))

#         event = get_object_or_404(Event, id=event_id)

#         # 取得所有簽到的使用者
#         checked_in_users = Registration.objects.filter(
#             event=event, status="registered"
#         ).values_list("user_id", "user__username")

#         # 取得所有已經中獎的使用者
#         existing_winners = Winner.objects.filter(event=event).values_list("user_id", flat=True)

#         # 只從未中獎的人裡面抽
#         eligible_users = [user for user in checked_in_users if user[0] not in existing_winners]

#         if len(eligible_users) < num_winners:
#             return render(request, 'draw_detail.html', {
#                 "winners": [], "error": "可抽獎人數不足"
#             })

#         # 隨機選擇中獎者
#         selected_winners = random.sample(eligible_users, num_winners)
#         winners_list = []
#         for user in selected_winners:
#             Winner.objects.create(event=event, user_id=user[0])
#             winners_list.append({"name": user[1]})

#         return render(request, 'draw_detail.html', {"winners": winners_list})

#     return redirect('draw_home')
from events.decorators import has_event_permission

@login_required
def draw_winners(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        num_winners = int(request.POST.get("num_winners", 1))

        event = get_object_or_404(Event, id=event_id)
        user = request.user

        # ✅ 權限檢查：活動負責人或後台管理員
        if not (user.is_staff or user in event.managers.all()):
            return render(request, '403.html', status=403)

        checked_in_users = Registration.objects.filter(
            event=event, status="registered"
        ).values_list("user_id", "user__username")

        existing_winners = Winner.objects.filter(event=event).values_list("user_id", flat=True)

        eligible_users = [user for user in checked_in_users if user[0] not in existing_winners]

        if len(eligible_users) < num_winners:
            return render(request, 'draw_detail.html', {
                "winners": [], "error": "可抽獎人數不足"
            })

        selected_winners = random.sample(eligible_users, num_winners)
        winners_list = []
        for user in selected_winners:
            Winner.objects.create(event=event, user_id=user[0])
            winners_list.append({"name": user[1]})

        return render(request, 'draw_detail.html', {"winners": winners_list})

    return redirect('draw_home')

# 回饋管理
@login_required
def feedback_dashboard(request):
    registrations = Registration.objects.filter(
        user=request.user,
        status='registered',
        check_in_time__isnull=False  # ✅ 有簽到時間
    )
    return render(request, 'feedback/dashboard.html', {'registrations': registrations})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from events.models import Event, Registration
from feedback.models import Form, Question, Response, Answer

@login_required
def fill_form(request, event_id):
    # 取得活動物件
    event = get_object_or_404(Event, pk=event_id)

    # 取得已報名且已簽到的使用者報名資料
    registration = get_object_or_404(
        Registration,
        user=request.user,
        event=event,
        status='registered',
        check_in_time__isnull=False
    )

    # 取得該活動的問卷
    form = get_object_or_404(Form, event=event)

    # ✅ 正確抓法：取得該問卷所有問題（不管有沒有被回答過）
    questions = form.questions.all()

    # ✅ 防止重複填寫
    if Response.objects.filter(form=form, registration=registration).exists():
        return render(request, 'feedback/already_filled.html', {'event': event})

    if request.method == 'POST':
        response = Response.objects.create(form=form, registration=registration)
        for question in questions:
            answer = request.POST.get(f'q_{question.id}', '')
            Answer.objects.create(response=response, question=question, content=answer)
        return render(request, 'feedback/thank_you.html')

    # 渲染問卷填寫頁
    return render(request, 'feedback/fill_form.html', {
        'event': event,
        'questions': questions,
    })
from django.db.models import Avg
from collections import Counter
import json

# @user_passes_test(lambda u: u.is_staff)
# def form_analysis(request, event_id):
#     form = get_object_or_404(Form, event_id=event_id)
#     questions = form.questions.all()
#     responses = Response.objects.filter(form=form)

#     total_registrants = Registration.objects.filter(event=form.event, status='registered').count()
#     total_responses = responses.count()
#     response_rate = round((total_responses / total_registrants) * 100, 2) if total_registrants > 0 else 0

#     # 預設取第一題為評分題
#     first_rating_q = questions.filter(question_type='rating').first()
#     avg_score = None
#     if first_rating_q:
#         avg_score = Answer.objects.filter(
#             question=first_rating_q,
#             response__form=form
#         ).aggregate(avg=Avg('content'))['avg']

#     # 整理每題答案列表
#     answers = {
#         q: Answer.objects.filter(question=q, response__form=form)
#         for q in questions
#     }
#     # 整理問答題答案（避免 template 裡 index dict）
#     text_answers = []
#     for q in questions:
#         if q.question_type == 'text':
#             text_answers.append({
#                 'question': q,
#                 'answers': Answer.objects.filter(question=q, response__form=form)
#             })

#     # 建立 Chart.js 資料格式
#     chart_data = {}
#     for q in questions:
#         if q.question_type in ['rating', 'single_choice']:
#             counter = Counter(a.content for a in answers[q])
#             chart_data[q.id] = dict(counter)

#     return render(request, 'feedback/form_analysis.html', {
#         'form': form,
#         'questions': questions,
#         'responses': responses,
#         'answers': answers,  # 給圖表用
#         'avg_score': avg_score,
#         'response_rate': response_rate,
#         'chart_data': json.dumps(chart_data),
#         'text_answers': text_answers,  # 新增的
#     })
@login_required
def form_analysis(request, event_id):
    form = get_object_or_404(Form, event_id=event_id)
    event = form.event

    # 權限檢查：管理員或活動的其中一位負責人才可以看
    if not (request.user.is_staff or request.user in event.managers.all()):
        return render(request, '403.html', status=403)

    questions = form.questions.all()
    responses = Response.objects.filter(form=form)

    total_registrants = Registration.objects.filter(event=event, status='registered').count()
    total_responses = responses.count()
    response_rate = round((total_responses / total_registrants) * 100, 2) if total_registrants > 0 else 0

    first_rating_q = questions.filter(question_type='rating').first()
    avg_score = Answer.objects.filter(
        question=first_rating_q,
        response__form=form
    ).aggregate(avg=Avg('content'))['avg'] if first_rating_q else None

    answers = {
        q: Answer.objects.filter(question=q, response__form=form)
        for q in questions
    }

    text_answers = []
    for q in questions:
        if q.question_type == 'text':
            text_answers.append({
                'question': q,
                'answers': Answer.objects.filter(question=q, response__form=form)
            })

    chart_data = {}
    for q in questions:
        if q.question_type in ['rating', 'single_choice']:
            counter = Counter(a.content for a in answers[q])
            chart_data[q.id] = dict(counter)

    return render(request, 'feedback/form_analysis.html', {
        'form': form,
        'questions': questions,
        'responses': responses,
        'answers': answers,
        'avg_score': avg_score,
        'response_rate': response_rate,
        'chart_data': json.dumps(chart_data),
        'text_answers': text_answers,
    })
