from django.core.files.storage import FileSystemStorage
from django.db.models import Prefetch
from django.shortcuts import render

# Create your views here.
# analizar metodos
from rest_framework import viewsets, generics

from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.decorators import api_view
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

from bs4 import BeautifulSoup

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

    def put(self, request, pk=None):
        print('pk', pk)
        #print(str(request.data['html_text']))

        """Consultas"""
        tag_learning_object = TagPageLearningObject.objects.get(pk =pk);
        page_learning_object = PageLearningObject.objects.get(pk = tag_learning_object.page_learning_object_id);

        tag_class_ref = tag_learning_object.id_class_ref
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)

        """WebScraping"""
        html_img_code = file_html.find_all(class_= tag_class_ref)

        if( (not request.data['text'].isspace()) & (request.data['text'] != "") ):
            text_update = request.data['text'];
            html_img_code[0]['alt'] = text_update;
            print("update", str(page_learning_object.preview_path))
            bsd.generate_new_htmlFile(file_html, page_learning_object.path)
            return Response({'message':'update successful'},status= status.HTTP_200_OK)
        return Response({'message':'Internal server error'}, status = status.HTTP_304_NOT_MODIFIED)

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

        print("request data", str(request.data))

        div_soup_data, id_ref = bsd.templateAdaptationTag(tag_page_learning_object.id_class_ref)
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find('p', tag_page_learning_object.id_class_ref)
        tag.append(div_soup_data)

        if 'text' in request.data:
            if request.data['text'] != '':
                button_text_data, button_text_tag_id = bsd.templateAdaptedTextButton(
                    tag_page_learning_object.id_class_ref,
                    request.data['text'])
                div_soup_data = tag.find(id=id_ref)
                # div_soup_data.append(button_text_data)
                div_soup_data.insert(1, button_text_data)

        if 'file' in request.data:
            # print(request.data['file'])

            file = request.data['file']

            file_name = file._name.split('.')
            file._name = bsd.getUUID() + '.' + file_name[-1]

            path = os.path.join(BASE_DIR, learning_object.path_adapted, 'oer_resources')
            path_src = os.path.join('oer_resources', file.name).replace("\\", "/")
            # print(path)
            save_path, path_system = ba.save_uploaded_file(path, file, learning_object.path_adapted, request)

            button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
                tag_page_learning_object.id_class_ref, path_src)
            div_soup_data = tag.find(id=id_ref)
            # div_soup_data.append(button_audio_data)
            div_soup_data.insert(len(div_soup_data) - 1, button_audio_data)

            serializer.save(
                type="p",
                id_ref=id_ref,
                path_src=path_src,
                path_preview=save_path,
                path_system=path_system,
            )

        else:
            serializer.save(
                type="p",
                id_ref=id_ref,
            )

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
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

        print("request data", str(request.data))

        # update tag adapted
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag_adaptation = file_html.find(id=tag_adapted.id_ref)
        #tag_adaptation.clear()
        # tag.append(div_soup_data)

        print("tag_adaptation"+str(tag_adaptation))


        if 'text' in request.data:
            button_text_data, button_text_tag_id = bsd.templateAdaptedTextButton(tag_page_learning_object.id_class_ref,
                                                                                 request.data['text'])

            print("button_text_data"+str(button_text_data))

            # tag_adaptation.insert(0, button_text_data).decompose()
            tag_text = tag_adaptation.find('input', "text")
            if tag_text is not None:
                tag_text.decompose()
            tag_adaptation.insert(1, button_text_data)



            print("tag_children"+str(tag_text))

            #tag = tag_adaptation.find(id=tag_adapted.button_text_id)
            #tag.replace_with(button_text_data)

            #print(tag_adaptation)

        if 'file' in request.data:

            if (tag_adapted.path_system != '') and (tag_adapted.path_system is not None):
                print("tag adapted " + str(tag_adapted.path_system))
                ba.remove_uploaded_file(tag_adapted.path_system)

            file = request.data['file']
            file._name = file.name.replace(" ", "")
            path = os.path.join(BASE_DIR, learning_object.path_adapted, 'oer_resources')
            path_src = os.path.join('oer_resources', file.name).replace("\\", "/")
            save_path, path_system = ba.save_uploaded_file(path, file, learning_object.path_adapted, request)

            button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
                tag_page_learning_object.id_class_ref, path_src)

            tag_audio = tag_adaptation.find('input', "audio")
            if tag_audio is not None:
                tag_audio.decompose()
            tag_adaptation.insert(len(tag_adaptation) - 1, button_audio_data)

            serializer.save(
                path_src=path_src,
                path_preview=save_path,
                path_system=path_system,

            )

        else:
            serializer.save()

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return Response(serializer.data)


@api_view(['POST'])
def paragraph_api_view(request, pk=None):
    if request.method == 'POST':
        return Response({"status": "ok"})
    pass


@api_view(['POST'])
def image_api_view(request, pk=None):
    if request.method == 'POST':
        return Response({"status": "ok"})
    pass


@api_view(['POST'])
def video_api_view(request, pk=None):
    if request.method == 'POST':
        return Response({"status": "ok"})
    pass


@api_view(['POST'])
def audio_api_view(request, pk=None):
    if request.method == 'POST':
        return Response({"status": "ok"})
    pass


@api_view(['POST'])
def button_api_view(request, pk=None):
    if request.method == 'POST':
        learning_object = get_object_or_404(LearningObject, pk=pk)
        files = bsd.read_html_files(os.path.join(BASE_DIR, learning_object.path_adapted))

        if request.data['value']:
            print("true value")
            print(request.data)
            print(pk)

            ba.add_files_adaptation(files, learning_object.path_adapted, True)

            return Response({"status": "ok", "operation": "add"})

        else:
            print("else value")
            ba.remove_button_adaptation(files, learning_object.path_adapted)
            return Response({"status": "ok", "operation": "remove"})
