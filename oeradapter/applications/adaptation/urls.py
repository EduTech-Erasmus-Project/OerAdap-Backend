from django.urls import path
from . import views

urlpatterns = [
    path('page/<int:pk>', views.PageRetrieveAPIView.as_view()),
    path('page/paragraph/<int:pk>', views.ParagraphView.as_view()),
    path('page/image/<int:pk>', views.ImageView.as_view()),
    path('page/video/<int:pk>', views.IframeView.as_view()),
    path('page/audio/<int:pk>', views.AudioView.as_view()),
    path('page/audio', views.AudioviewCreate.as_view()),

    path('adapted/tag/<int:pk>', views.returnObjectsAdapted.as_view()),
    path('compress/learningObject/<int:pk>', views.comprimeFileZip),
    path('convert/paragraph/<int:pk>', views.CovertTextToAudioRetrieveAPIView.as_view()),

    path('adapter/image/preview/<int:pk>', views.AdaptedImagePreviewRetrieveUpdateAPIView.as_view()),
    path('adapter/image/<int:pk>', views.AdapatedImageView.as_view()),
    path('adapter/paragraph/<int:pk>', views.AdapterParagraphTestRetrieveAPIView.as_view()),

    path('adapter/video/subtitle/generate/<int:pk>', views.VideoGenerateCreateAPIView.as_view()),
    path('adapter/video/subtitle/add/<int:pk>', views.VideoAddCreateAPIView.as_view()),
    path('adapter/gettranscript/<int:pk>', views.transcript_api_view),
    path('adapter/updatetranscript/<int:pk>', views.update_transcript_api_view),

    path('revert/image/<int:pk>', views.revertImageRetrieveUpdateAPIView.as_view()),
    path('revert/audio/<int:pk>', views.revertAudioRetrieveUpdateAPIView.as_view()),
    path('revert/paragraph/<int:pk>', views.revertParagraphRetrieveUpdateAPIView.as_view()),
    path('revert/video/<int:pk>', views.revertVideoRetrieveUpdateAPIView.as_view()),
]


