from django.db.models import Prefetch
from django.shortcuts import render

# Create your views here.
# analizar metodos
from rest_framework import viewsets, generics
from rest_framework.generics import RetrieveAPIView
from . import serializers
from ..learning_object.models import TagPageLearningObject

from rest_framework import status
from rest_framework.response import Response


class ParagraphView(RetrieveAPIView):
    queryset = TagPageLearningObject.objects.all()
    serializer_class = serializers.TagLearningObjectDetailSerializerP

class ImageView(RetrieveAPIView):
    queryset = TagPageLearningObject.objects.all()
    serializer_class = serializers.TagLearningObjectDetailSerializerI

class IframeView(RetrieveAPIView):
    queryset = TagPageLearningObject.objects.all()
    serializer_class = serializers.TagLearningObjectDetailSerializerIf






