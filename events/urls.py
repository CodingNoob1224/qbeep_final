
from django.urls import path
from . import views
urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/register/', views.register_event, name='register_event'),
    path('<int:event_id>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('admin/edit_event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),  
    path('check-in/<int:event_id>/', views.check_in_page, name='check_in_page'),
    path('check-in-user/<int:event_id>/', views.check_in_user, name='check_in_user'),
    path('feedback/analysis/<int:event_id>/', views.event_analysis, name='event_analysis'),
    path('<int:event_id>/check-out/', views.check_out_page, name='check_out_page'),
    path('<int:event_id>/check-out-user/', views.check_out_user, name='check_out_user'),
]
