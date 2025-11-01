"""
URL маршруты для sessions app
"""

from django.urls import path
from . import views

app_name = 'sessions'

urlpatterns = [
    path('current/', views.current_session, name='current'),
    path('list/', views.SessionListView.as_view(), name='list'),
]