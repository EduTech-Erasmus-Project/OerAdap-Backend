from django.db.models import Prefetch
from django.shortcuts import render

# Create your views here.
# analizar metodos
from rest_framework import viewsets, generics
from rest_framework.generics import RetrieveAPIView, GenericAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import JSONParser

from . import serializers
from ..learning_object.models import TagPageLearningObject
from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response


class ParagraphView(RetrieveAPIView):
    #serializer_class = serializers.TagLearningObjectDetailSerializerP
    def get(self, request, pk=None):

        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & Q(tag='p'))
        pages = serializers.TagsSerializer(pages, many=True)
        #print(pages.data)

        if len(pages.data):
            return Response(pages.data)

        return Response( {
           'message':"the page has no paragraphs"
        }, status=status.HTTP_404_NOT_FOUND)
   # def get_queryset(self):
    #    return self.get_serializer().Meta.model.objects.all()

class ImageView(RetrieveAPIView):

    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object=pk) & Q(tag='img'))
        pages = serializers.TagsSerializerImage(pages, many=True)

        if len(pages.data):
            def get_queryset(self):
                pages = super().get_queryset()
                pages = pages.prefetch_related(
                    Prefetch('atributes')
                )
            return Response(pages.data)

        return Response({
            'message': "the page has no images"
        }, status=status.HTTP_404_NOT_FOUND)

class ImageView(RetrieveAPIView):

    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object=pk) & Q(tag='img'))
        pages = serializers.TagsSerializerImage(pages, many=True)

        if len(pages.data):
            def get_queryset(self):
                pages = super().get_queryset()
                pages = pages.prefetch_related(
                    Prefetch('atributes')
                )
            return Response(pages.data)

        return Response({
            'message': "the page has no images"
        }, status=status.HTTP_404_NOT_FOUND)

#class ImageViewOneObject(RetrieveUpdateAPIView):
    #def update(self, request, pk=None):
        #pages = TagPageLearningObject.objects.filter(Q(id=pk) & Q(tag='img'))


class IframeView(RetrieveAPIView):
    def get(self, request,pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & (Q(tag='iframe') | Q(tag='video')))
        pages = serializers.TagsSerializer(pages, many=True)
        if len(pages.data):
            return Response(pages.data)

        return Response({
            'message': "the page has no (video | iframe)"
        }, status=status.HTTP_404_NOT_FOUND)

class AudioView(RetrieveAPIView):
    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & Q(tag='audio'))
        pages = serializers.TagsSerializer(pages, many=True)
        if len(pages.data):
            return Response(pages.data)
        return Response({
            'message': "the page has no audio"
        }, status=status.HTTP_404_NOT_FOUND)








