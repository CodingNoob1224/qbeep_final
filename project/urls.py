from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # 導入 TemplateView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),  # 使用 TemplateView 直接渲染 index.html
    path('admin/', admin.site.urls),
    path('events/', include('events.urls')),
    path('member/', include('member.urls')),
    path('events/', include('events.urls')),  # 確保註冊了 events 應用的路由

    # 你可以為其他應用添加路由
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
