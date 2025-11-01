"""
smart_award URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/sessions/', include('apps.sessions.urls')),
    path('api/v1/votes/', include('apps.voting.urls')),
    path('api/v1/results/', include('apps.results.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/export/', include('apps.analytics.export_urls')),
    path('api/v1/settings/', include('apps.core.urls')),
    path('api/v1/logs/', include('apps.core.audit_urls')),
    
    # Telegram Bot Webhook
    path('telegram/', include('apps.telegram_bot.urls')),
    
    # OAuth2
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    
    # Health check
    path('health/', include('apps.core.health_urls')),
    
    # API Documentation (if using DRF spectacular)
    # path('api/docs/', SpectacularAPIView.as_view(), name='schema'),
    # path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add Django Debug Toolbar if installed
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Custom error handlers
handler400 = 'apps.core.views.bad_request'
handler403 = 'apps.core.views.permission_denied'
handler404 = 'apps.core.views.page_not_found'
handler500 = 'apps.core.views.server_error'

# Admin site customization
admin.site.site_header = "Система \"Умная премия\""
admin.site.site_title = "Smart Award Admin"
admin.site.index_title = "Панель администрирования"