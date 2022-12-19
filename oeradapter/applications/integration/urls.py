from django.urls import path, include
from . import views

urlpatterns = [
    path('receive_file/', views.receive_file),
]
