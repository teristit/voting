"""
URL маршруты для results app
"""

from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('my/', views.my_results, name='my_results'),
    path('session/<int:session_id>/', views.session_results, name='session_results'),
]