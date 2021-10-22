from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('page/paragraph/<int:pk>', views.ParagraphView.as_view()),
    path('page/image/<int:pk>', views.ImageView.as_view()),
    path('page/iframe/<int:pk>', views.IframeView.as_view()),
]