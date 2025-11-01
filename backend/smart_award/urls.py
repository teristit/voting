"""
smart_award URL Configuration
Подключены API приложения и админка.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/sessions/', include('apps.sessions.urls')),
    path('api/v1/voting/', include('apps.voting.urls')),
    path('api/v1/results/', include('apps.results.urls')),
]

# Статические и медиа в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Кастомные подписи админки
admin.site.site_header = "Система \"Умная премия\""
admin.site.site_title = "Smart Award Admin"
admin.site.index_title = "Панель администрирования"