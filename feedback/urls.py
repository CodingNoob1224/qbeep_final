# feedback/urls.py
from django.urls import path
from . import views
from .views import check_detail
from .views import draw_home, draw_winners


urlpatterns = [
    path('event/<int:event_id>/', views.check_detail, name='check_detail'),  # 修改為 check_detail
    path('event_analysis/', views.event_analysis, name='event_analysis'),
    path('event/<int:event_id>/', check_detail, name='check_detail'),
    path('draw/', draw_home, name='draw_home'),
    path('draw_winners/<int:event_id>/', draw_winners, name='draw_winners'),
]

