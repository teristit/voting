"""
URL маршруты для users app
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.user_profile, name='profile'),
    path('list/', views.UserListView.as_view(), name='list'),
]