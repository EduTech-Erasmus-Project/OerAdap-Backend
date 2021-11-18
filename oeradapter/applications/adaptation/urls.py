from django.urls import path, re_path, include
from . import views


urlpatterns = [
    path('page/<int:pk>', views.PageRetrieveAPIView.as_view()),
    path('page/paragraph/<int:pk>', views.ParagraphView.as_view()),
    path('page/image/<int:pk>', views.ImageView.as_view()),
    path('page/video/<int:pk>', views.IframeView.as_view()),
    path('page/audio/<int:pk>', views.AudioView.as_view()),
    path('page/audio', views.AudioviewCreate.as_view()),

    path('compress/learningObject/<int:pk>',views.comprimeFileZip().as_view()),
    path('convert/paragraph/<int:pk>', views.CovertText_Audio_View.as_view()),

    path('adapter/image/<int:pk>', views.AdapatedImageView.as_view()),
    path('adapter/paragraph/', views.AdapterParagraphCreateAPIView.as_view()),
    path('adapter/paragraph/<int:pk>', views.AdapterParagraphRetrieveAPIView.as_view()),

    #path('adapter/video/subtitle/<int:pk>', views.TranscriptJsonRetrieveAPIView.as_view()),
    path('adapter/video/subtitle/generate/<int:pk>', views.VideoGenerateCreateAPIView.as_view()),
    path('adapter/gettranscript/<int:pk>', views.transcript_api_view),


    #path('adapter/video/subtitle/<int:pk>', views.VideoGenericAPIView.as_view()),

    # Urls config adaptation
    # path('config/paragraph/<int:pk>', views.paragraph_api_view),
    # path('config/image/<int:pk>', views.image_api_view),
    # path('config/video/<int:pk>', views.video_api_view),
    # path('config/audio/<int:pk>', views.audio_api_view),
    # path('config/button/<int:pk>', views.button_api_view),
]