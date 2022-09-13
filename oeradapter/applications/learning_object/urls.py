from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('learning_objects/', views.LearningObjectCreateApiView.as_view()),
    path('learning_objects/<int:pk>', views.LearningObjectRetrieveAPIView.as_view()),

    path('learning_objects/audio/<int:pk>', views.LearningObjectAudioRetrieveAPIView.as_view()),
    path('learning_objects/image/<int:pk>', views.LearningObjectImageRetrieveAPIView.as_view()),
    path('learning_objects/video/<int:pk>', views.LearningObjectVideoRetrieveAPIView.as_view()),

    path('requestapi/', views.RequestApiEmail.as_view()),
    path('contact/', views.email_contact_api_view),

    path('metadata_info/', views.MetadataInfoListAPIView.as_view()),

    path('v1/oeradapter/upload', views.api_upload),
    path('v1/oeradapter/files', views.api_get_files),
    path('v1/oeradapter/files/<int:pk>', views.api_get_file),

    path('', include('applications.adaptation.urls'))
]
