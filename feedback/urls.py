# feedback/urls.py
from django.urls import path
from . import views
from .views import check_detail
from .views import draw_home, draw_winners


urlpatterns = [
    path('event/<int:event_id>/', views.check_detail, name='check_detail'),
    path('event_analysis/', views.event_analysis, name='event_analysis'),
    path('draw/', draw_home, name='draw_home'),
    path('draw_winners/', draw_winners, name='draw_winners'),
    path('forms/', views.feedback_dashboard, name='dashboard'),
    path('forms/<int:event_id>/fill/', views.fill_form, name='fill_form'),
    path('forms/<int:event_id>/analysis/', views.form_analysis, name='form_analysis'),

]
