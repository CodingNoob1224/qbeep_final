from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 
from .views import register
urlpatterns = [
    path("register/", register, name="register"),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/create_event/', views.create_event, name='create_event'),  # 確保這裡有 create_event 的路由
]


