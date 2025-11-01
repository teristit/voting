"""
URL маршруты для voting app
"""

from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('cast/', views.cast_votes, name='cast_votes'),
    path('my/', views.my_votes, name='my_votes'),
]