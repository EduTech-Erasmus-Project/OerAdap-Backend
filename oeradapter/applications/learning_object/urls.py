from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'learning_objects', views.UploadFileViewSet, basename='learning_objects')
router.register(r'adaptation_settings', views.LearningObjectAdaptationSettingsViewSet, basename='adaptation_settings')

urlpatterns = router.urls
