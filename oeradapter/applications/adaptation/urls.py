from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('page/paragraph/<int:pk>', views.ParagraphView.as_view()),
    path('page/image/<int:pk>', views.ImageView.as_view()),
    #path('page/image/update/<int:pk>', views.ImageViewOneObject.as_view()),
    path('page/video/<int:pk>', views.IframeView.as_view()),
    path('page/audio/<int:pk>', views.AudioView.as_view()),
]