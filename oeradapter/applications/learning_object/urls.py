from django.urls import path
from . import views
app_name = 'learning_object_app'

urlpatterns = [
    path('api/upload/', views.UploadLearningObject.as_view(), name='upload')
]