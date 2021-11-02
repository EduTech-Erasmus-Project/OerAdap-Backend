from django.core.files.storage import FileSystemStorage
from django.db.models import Prefetch
from django.shortcuts import render

# Create your views here.
# analizar metodos
from rest_framework import viewsets, generics
from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView
from unipath import Path
from shutil import copyfile
from . import serializers
from .serializers import TagAdaptedSerializer
from ..learning_object.models import TagPageLearningObject, TagAdapted, PageLearningObject, LearningObject
from django.db.models import Q
import os

from django.shortcuts import get_object_or_404
from django.core.files import File

from rest_framework import status
from rest_framework.response import Response

from ..helpers_functions import beautiful_soup_data as bsd
from ..helpers_functions import base_adaptation as ba

BASE_DIR = Path(__file__).ancestor(3)


class ParagraphView(RetrieveAPIView):
    # serializer_class = serializers.TagLearningObjectDetailSerializerP
    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & Q(tag='p'))
        pages = serializers.TagsSerializer(pages, many=True)
        # print(pages.data)

        if len(pages.data):
            return Response(pages.data)

        return Response({
            'message': "the page has no paragraphs"
        }, status=status.HTTP_404_NOT_FOUND)


# def get_queryset(self):
#    return self.get_serializer().Meta.model.objects.all()

class ImageView(RetrieveAPIView):
    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & Q(tag='img'))
        pages = serializers.TagsSerializer(pages, many=True)
        if len(pages.data):
            return Response(pages.data)

        return Response({
            'message': "the page has no images"
        }, status=status.HTTP_404_NOT_FOUND)


class IframeView(RetrieveAPIView):
    def get(self, request, pk=None):
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


class AdapterParagraphCreateAPIView(CreateAPIView):
    serializer_class = TagAdaptedSerializer

    def post(self, request, *args, **kwargs):
        """Post adapted tag"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tag_page_learning_object = TagPageLearningObject.objects.get(pk=request.data['tag_page_learning_object'])
        page_learning_object = PageLearningObject.objects.get(pk=tag_page_learning_object.page_learning_object_id)
        learning_object = LearningObject.objects.get(pk=page_learning_object.learning_object_id)

        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        id_ref = bsd.getUUID()

        if 'file' in request.data:
            print(request.data['file'])
            file = request.data['file']
            file._name = file.name.replace(" ", "")
            path = os.path.join(BASE_DIR, learning_object.path_adapted, 'oer_resouces')
            path_src = os.path.join('oer_resouces', file.name)
            # print(path)
            save_path, path_system = ba.save_uploaded_file(path, file, learning_object.path_adapted, request)

            serializer.save(
                type="p",
                id_ref=id_ref,
                path_src=path_src,
                path_preview=save_path,
                path_system=path_system
            )

        else:
            serializer.save(
                type="p",
                id_ref=id_ref,
            )

        return Response(serializer.data)


class AdapterParagraphRetrieveAPIView(RetrieveUpdateAPIView):
    serializer_class = TagAdaptedSerializer

    def get(self, request, pk=None):
        """Get tag adapted by paragraph pk"""
        tag_adapted = get_object_or_404(TagAdapted, tag_page_learning_object_id=pk)
        serializer = self.get_serializer(tag_adapted)
        return Response(serializer.data)

    def update(self, request, pk=None):
        print("Update data")
        tag_adapted = get_object_or_404(TagAdapted, pk=pk)
        serializer = TagAdaptedSerializer(instance=tag_adapted, data=request.data)
        serializer.is_valid(raise_exception=True)

        tag_page_learning_object = TagPageLearningObject.objects.get(pk=tag_adapted.tag_page_learning_object_id)
        page_learning_object = PageLearningObject.objects.get(pk=tag_page_learning_object.page_learning_object_id)
        learning_object = LearningObject.objects.get(pk=page_learning_object.learning_object_id)

        if 'file' in request.data:

            if (tag_adapted.path_system is not '') and (tag_adapted.path_system is not None):
                print("tag adapted "+str(tag_adapted.path_system))
                ba.remove_uploaded_file(tag_adapted.path_system)

            file = request.data['file']
            file._name = file.name.replace(" ", "")
            path = os.path.join(BASE_DIR, learning_object.path_adapted, 'oer_resouces')
            path_src = os.path.join('oer_resouces', file.name)
            save_path, path_system = ba.save_uploaded_file(path, file, learning_object.path_adapted, request)

            serializer.save(
                path_src=path_src,
                path_preview=save_path,
                path_system=path_system
            )

        else:
            serializer.save()

        return Response(serializer.data)
