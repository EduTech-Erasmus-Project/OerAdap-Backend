
from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('learning_objects/', views.LearningObjectCreateApiView.as_view()),
    path('learning_objects/<int:pk>', views.LearningObjectRetrieveAPIView.as_view()),

]