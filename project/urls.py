from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # 導入 TemplateView

from django.conf import settings
from django.conf.urls.static import static

from events import views  # 確保 views 被正確 import

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),  # 渲染 index.html
    path('admin/', admin.site.urls),
    path('events/', include('events.urls')),  # 註冊 events 的路由
    path('member/', include('member.urls')),  # 註冊 member 的路由
    path('feedback/', include('feedback.urls')),  # 註冊 feedback 的路由

    # 簽到與簽退
    path('events/check-in/<int:event_id>/', views.check_in_page, name='check_in_page'),
    path('events/check-out/<int:event_id>/', views.check_out_page, name='check_out_page'),  # 新增簽退
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
