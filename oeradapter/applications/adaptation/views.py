from django.db.models import Prefetch
from django.shortcuts import render

# Create your views here.
# analizar metodos
from rest_framework import viewsets

from .serializers import PageLearningObjectSerializer
from ..learning_object.models import PageLearningObject


class PageOAViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageLearningObject.objects.all()
    serializer_class = PageLearningObjectSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related(
            Prefetch('tags')
        )
        return queryset


