from django.core.files.storage import FileSystemStorage
from django.db.models import Prefetch
from django.shortcuts import render
import json
# Create your views here.
# analizar metodos
from psycopg2._psycopg import adapt
from rest_framework import viewsets, generics

from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, GenericAPIView

from rest_framework.decorators import api_view
from setuptools.command.alias import alias
from unipath import Path
from shutil import copyfile
from . import serializers
from .serializers import TagAdaptedSerializer, PagesDetailSerializer, TagsVideoSerializer, TagAdaptedVideoSerializer, \
    TagAdaptedAudioSerializer
from ..learning_object.models import TagPageLearningObject, TagAdapted, PageLearningObject, LearningObject, \
    DataAttribute, Transcript
from django.db.models import Q
import os

from django.shortcuts import get_object_or_404
from django.core.files import File

from rest_framework import status
from rest_framework.response import Response

from ..helpers_functions import beautiful_soup_data as bsd
from ..helpers_functions import base_adaptation as ba
import shutil

# Conversion de audio a texto

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
        # pages = TagAdapted.objects.filter(tag_page_learning_object=pages_id.id)
        pages = serializers.TagsSerializerTagAdapted(pages, many=True)

        if len(pages.data):
            def get_queryset(self):
                pages = super().get_queryset()
                pages = pages.prefetch_related(
                    Prefetch('attributes')
                )

            def get_queryset(self):
                pages = super().get_queryset()
                pages = pages.prefetch_related(
                    Prefetch('tags_adapted')
                )

            return Response(pages.data)

        return Response({
            'message': "the page has no images"
        }, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk=None):
        # print(str(request.data['html_text']))
        """Consultas"""
        tag_learning_object = TagPageLearningObject.objects.get(pk=pk);
        page_learning_object = PageLearningObject.objects.get(pk=tag_learning_object.page_learning_object_id);
        tag_adapted_learning_object = TagAdapted.objects.get(tag_page_learning_object=tag_learning_object.id);

        tag_class_ref = tag_adapted_learning_object.id_ref
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)

        """WebScraping"""
        html_img_code = file_html.find_all(class_=tag_class_ref)
        text_update = request.data['text'];
        alt_db_aux = bsd.convertElementBeautifulSoup(str(tag_adapted_learning_object.html_text))
        alt_db_aux = alt_db_aux.img
        alt_db_aux['alt'] = text_update
        tag_adapted_learning_object.html_text = str(alt_db_aux)

        """Validacion de envio de datos, para realizar la actualizacion """
        if ((not request.data['text'].isspace()) & (request.data['text'] != "")):
            """ Guardar en la base de datos"""
            adapted_serializer = TagAdaptedSerializer(tag_adapted_learning_object, data=request.data)
            if adapted_serializer.is_valid():
                html_img_code[0]['alt'] = text_update;
                """Revisar si el elemento ya esta envuelto por el elemto figure"""
                if html_img_code[0].parent.name != 'figure':
                    replace_html_code = bsd.templateAdaptionImage(html_img_code, tag_learning_object.id_class_ref)
                    html_img_code[0].replace_with(replace_html_code)
                else:
                    replace_description = bsd.convertElementBeautifulSoup('<em>' + text_update + "</em>")
                    html_img_code[0].parent.em.replace_with(replace_description.em)
                print('path', page_learning_object.preview_path)
                bsd.generate_new_htmlFile(file_html, page_learning_object.path)
                adapted_serializer.save()
                return Response(adapted_serializer.data)
        return Response({'message': 'Internal server error'}, status=status.HTTP_304_NOT_MODIFIED)


class AdapatedImageView(RetrieveUpdateAPIView):
    serializer_class = TagAdaptedSerializer

    def get(self, request, pk=None):
        """Get tag adapted by paragraph pk"""
        tag_adapted = get_object_or_404(TagAdapted, tag_page_learning_object_id=pk)
        serializer = self.get_serializer(tag_adapted)
        return Response(serializer.data)


class IframeView(RetrieveAPIView):
    serializer_class = TagsVideoSerializer

    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & (Q(tag='iframe') | Q(tag='video')))
        pages = self.get_serializer(pages,
                                    many=True)  # & (Q(tag_page_learning_object__tag='iframe') | Q(tag_page_learning_object__tag='video'))

        # data_attributes = DataAttribute.objects.filter(Q(tag_page_learning_object__page_learning_object_id=pk) & (Q(tag_page_learning_object__tag='iframe') | Q(tag_page_learning_object__tag='video')))
        # data_attributes = self.get_serializer(data_attributes, many=True)

        # print(data_attributes.data)

        return Response(pages.data)


class AudioviewCreate(RetrieveAPIView):
    def post(self, request, *args, **kwargs):
        """Consulta de datos"""
        pk = request.data['tag_page_learning_object']
        tag_learning_object = TagPageLearningObject.objects.get(pk=pk);
        page_learning_object = PageLearningObject.objects.get(pk=tag_learning_object.page_learning_object_id);
        audioSerializer = TagAdaptedSerializer(data=request.data)

        """Web Scraping"""
        div_soup_data, id_ref = bsd.templateAdaptationTag(tag_learning_object.id_class_ref);
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find('audio', tag_learning_object.id_class_ref)
        # tag['pTooltip']= 'Ver descripción visual de audio'
        print(tag)
        tag_aux = str(tag)
        tag.insert(1, div_soup_data)

        if str(request.data['method']) == 'create':
            if ((not request.data['text'].isspace()) & (request.data['text'] != "")):
                """Serializamos los datos para guardarlos en la base de datos"""

                if audioSerializer.is_valid():
                    audioSerializer.save()

                    button_text_data = bsd.templateAudioTextButton(
                        tag_learning_object.id_class_ref,
                        request.data['text'])
                    div_soup_data = tag.find(id=id_ref)
                    div_soup_data.insert(1, button_text_data)
                    tag_audio_div = bsd.templateAdaptedAudio(tag_aux, tag_learning_object.id_class_ref)
                    tag_audio_div.append(div_soup_data)
                    tag.replace_with(tag_audio_div)

                    bsd.generate_new_htmlFile(file_html, page_learning_object.path)
                    return Response(audioSerializer.data, status=status.HTTP_200_OK)
            return Response({'message': 'Internal server error'}, status=status.HTTP_304_NOT_MODIFIED)
        elif str(request.data['method']) == 'automatic':
            path = request.data['path_system']
            # print(request.data['path_system'])
            new_text = ba.convertAudio_Text(path)
            """Creamos un nuevo objeto adaptado ya que agregamos el texto ahora"""
            try:
                TagAdapted_create = TagAdapted.objects.create(
                    tag_page_learning_object_id=request.data['tag_page_learning_object'],
                    path_system=request.data['path_system'],
                    id_ref=request.data['id_ref'],
                    type=request.data['type'],
                    html_text=request.data['html_text'],
                    path_src=request.data['path_src'],
                    text=new_text
                )
                serializer = TagAdaptedSerializer(TagAdapted_create)

                button_text_data = bsd.templateAudioTextButton(
                    tag_learning_object.id_class_ref,
                    new_text)
                div_soup_data = tag.find(id=id_ref)
                div_soup_data.insert(1, button_text_data)
                tag_audio_div = bsd.templateAdaptedAudio(tag_aux, tag_learning_object.id_class_ref)
                tag_audio_div.append(div_soup_data)
                tag.replace_with(tag_audio_div)

                bsd.generate_new_htmlFile(file_html, page_learning_object.path)
            except:
                return Response({'message': 'audio is already adapted', 'status': 'false'},
                                status=status.HTTP_404_NOT_FOUND)

            return Response(serializer.data)

        return Response({'message': 'audio is already adapted', 'status': 'false'}, status=status.HTTP_404_NOT_FOUND)


class AudioView(RetrieveAPIView):
    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & Q(tag='audio'))
        pages = serializers.TagsSerializerTagAdapted(pages, many=True)
        if len(pages.data):
            def get_queryset(self):
                pages = super().get_queryset()
                pages = pages.prefetch_related(
                    Prefetch('tags_adapted')
                )

            return Response(pages.data)
        return Response({
            'message': "the page has no audio"
        }, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk=None):
        """Consultas"""
        tag_learning_object = TagPageLearningObject.objects.get(pk=pk)
        page_learning_object = PageLearningObject.objects.get(pk=tag_learning_object.page_learning_object_id)
        tag_adapted_learning_object = TagAdapted.objects.get(tag_page_learning_object=tag_learning_object.id)

        """Web Scraping"""
        tag_class_ref = tag_adapted_learning_object.id_ref
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        ref_change = file_html.find_all('input', id=str(tag_class_ref))
        text_adapted = request.data['text']
        onChange_ref = """textAdaptationEvent('""" + str(text_adapted) + """', '""" + tag_class_ref + """', this)"""
        """Validacion de envio de datos, para realizar la actualizacion """
        if ((not request.data['text'].isspace()) & (request.data['text'] != "")):
            """ Guardar en la base de datos"""
            adapted_serializer = TagAdaptedSerializer(tag_adapted_learning_object, data=request.data)
            if adapted_serializer.is_valid():
                """Cambiamos el texto en el html"""
                ref_change[0]['onclick'] = onChange_ref;
                bsd.generate_new_htmlFile(file_html, page_learning_object.path)
                adapted_serializer.save()
                return Response(adapted_serializer.data)

        return Response({'message': 'Internal server error'}, status=status.HTTP_304_NOT_MODIFIED)


class AdapterParagraphTestRetrieveAPIView(RetrieveUpdateAPIView):
    serializer_class = TagAdaptedAudioSerializer

    def get(self, request, pk=None):
        """Get tag adapted by paragraph pk"""
        tag_adapted = get_object_or_404(TagAdapted, tag_page_learning_object_id=pk)
        serializer = TagAdaptedAudioSerializer(tag_adapted)
        print(serializer.data)
        return Response(serializer.data)

    def post(self, request, pk=None):
        print("pk" + str(pk))
        tag_page_learning_object = get_object_or_404(TagPageLearningObject, pk=pk)
        page_learning_object = PageLearningObject.objects.get(type='adapted',
                                                              pk=tag_page_learning_object.page_learning_object_id)
        learning_object = LearningObject.objects.get(pk=page_learning_object.learning_object_id)
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)

        try:
            tag_adapted = TagAdapted.objects.get(tag_page_learning_object_id=pk)
            tag_adaptation = file_html.find(id=tag_adapted.id_ref)
            print("update")
            # update tag adapted
            if 'text' in request.data:
                if request.data['text'] != '':
                    button_text_data, button_text_tag_id = bsd.templateAdaptedTextButton(
                        tag_page_learning_object.id_class_ref,
                        request.data['text'])
                    tag_text = tag_adaptation.find('input', "text")
                    if tag_text is not None:
                        tag_text.decompose()
                    tag_adaptation.insert(1, button_text_data)
                    print(request.data['text'])
                    tag_adapted.text = request.data['text']
                    tag_adapted.html_text = request.data['html_text']
            if 'file' in request.data:
                if (tag_adapted.path_system != '') and (tag_adapted.path_system is not None):
                    print("tag adapted " + str(tag_adapted.path_system))
                    ba.remove_uploaded_file(tag_adapted.path_system)
                file = request.data['file']
                file._name = file.name.replace(" ", "")
                path = os.path.join(BASE_DIR, learning_object.path_adapted, 'oer_resources')
                path_src = os.path.join('oer_resources', file.name).replace("\\", "/")
                path_preview, path_system = ba.save_uploaded_file(path, file, learning_object.path_adapted, request)

                button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
                    tag_page_learning_object.id_class_ref, path_src)

                tag_audio = tag_adaptation.find('input', "audio")
                if tag_audio is not None:
                    tag_audio.decompose()
                tag_adaptation.insert(len(tag_adaptation) - 1, button_audio_data)

                tag_adapted.path_src = path_src
                tag_adapted.path_preview = path_preview
                tag_adapted.path_system = path_system

            bsd.generate_new_htmlFile(file_html, page_learning_object.path)
            tag_adapted.save()
            serializer = self.get_serializer(tag_adapted)
            return Response(serializer.data)
        except:
            print("Create")
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
                print(request.data['file'])

                file = request.data['file']

                file_name = file._name.split('.')
                file._name = bsd.getUUID() + '.' + file_name[-1]

                path = os.path.join(BASE_DIR, learning_object.path_adapted, 'oer_resources')
                path_src = os.path.join('oer_resources', file.name).replace("\\", "/")

                path_preview, path_system = ba.save_uploaded_file(path, file, learning_object.path_adapted, request)

                button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
                    tag_page_learning_object.id_class_ref, path_src)
                div_soup_data = tag.find(id=id_ref)
                # div_soup_data.append(button_audio_data)
                div_soup_data.insert(len(div_soup_data) - 1, button_audio_data)

                data = TagAdapted.objects.create(
                    type="p",
                    id_ref=id_ref,
                    path_src=path_src,
                    path_preview=path_preview,
                    path_system=path_system,
                    tag_page_learning_object=tag_page_learning_object
                )

            else:
                data = TagAdapted.objects.create(
                    text=request.data['text'],
                    html_text=request.data['html_text'],
                    type="p",
                    id_ref=id_ref,
                    tag_page_learning_object=tag_page_learning_object
                )

            serializer = TagAdaptedAudioSerializer(data)
            bsd.generate_new_htmlFile(file_html, page_learning_object.path)
            return Response(serializer.data)


class PageRetrieveAPIView(RetrieveAPIView):
    serializer_class = PagesDetailSerializer
    queryset = PageLearningObject.objects.all()


class CovertTextToAudioRetrieveAPIView(RetrieveAPIView):
    serializer_class = TagAdaptedAudioSerializer

    def get(self, request, pk=None):
        tag_page_learning_object = TagPageLearningObject.objects.get(pk=pk)
        page_learning_object = PageLearningObject.objects.get(pk=tag_page_learning_object.page_learning_object_id)
        learning_object = LearningObject.objects.get(pk=page_learning_object.learning_object_id)

        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)

        path_src, path_system, path_preview = ba.convertText_Audio(tag_page_learning_object.text,
                                                                   learning_object.path_adapted,
                                                                   tag_page_learning_object.id_class_ref, request)

        tag_adapted = None
        try:
            tag_adapted = TagAdapted.objects.get(tag_page_learning_object_id=pk)
        except:
            pass

        if tag_adapted is None:

            div_soup_data, id_ref = bsd.templateAdaptationTag(tag_page_learning_object.id_class_ref)
            tag = file_html.find('p', tag_page_learning_object.id_class_ref)
            tag.append(div_soup_data)

            button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
                tag_page_learning_object.id_class_ref, path_src)
            div_soup_data = tag.find(id=id_ref)
            div_soup_data.insert(len(div_soup_data) - 1, button_audio_data)

            data = TagAdapted.objects.create(
                type="p",
                id_ref=id_ref,
                path_src=path_src,
                path_preview=path_preview,
                path_system=path_system,
            )
            serializers = self.get_serializer(data)
        else:
            tag_adaptation = file_html.find(id=tag_adapted.id_ref)
            button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
                tag_page_learning_object.id_class_ref, path_src)

            tag_audio = tag_adaptation.find('input', "audio")
            if tag_audio is not None:
                tag_audio.decompose()
            tag_adaptation.insert(len(tag_adaptation) - 1, button_audio_data)

            tag_adapted.path_src = path_src
            tag_adapted.path_preview = path_preview
            tag_adapted.path_system = path_system

            tag_adapted.save()

            serializers = self.get_serializer(tag_adapted)
            # print(data)

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return Response(serializers.data)


class VideoGenerateCreateAPIView(CreateAPIView):
    serializer_class = TagAdaptedVideoSerializer

    def post(self, request, pk=None):
        # tag = TagPageLearningObject.objects.get(pk=pk)
        tag = get_object_or_404(TagPageLearningObject, pk=pk)
        captions = []
        transcripts = []
        try:
            tag_adapted = TagAdapted.objects.get(tag_page_learning_object_id=tag.id, type="video")
            subtitle = Transcript.objects.filter(tag_adapted_id=tag_adapted.id)

            print("tag adapted" + str(tag_adapted))

            sub_en = any(sub.srclang == "en" for sub in subtitle)
            sub_es = any(sub.srclang == "es" for sub in subtitle)

            print(sub_en)

            if sub_en:
                pass
            if sub_es:
                pass

            # print(len(subtitle))
            return Response({"status": "ready_tag_adapted"}, status=status.HTTP_200_OK)
        except:
            # learning_object = tag_adapted.objects.get(tag_page_learning_object__page_learning_object=)
            data_attribute = DataAttribute.objects.get(tag_page_learning_object_id=tag.id)
            learning_object = LearningObject.objects.get(pk=tag.page_learning_object.learning_object_id)
            print("path " + str(learning_object.path_adapted))

            if data_attribute.source == "local":
                # print("type local")
                return Response({"message": "Local translations under development", "code": "developing"},
                                status=status.HTTP_200_OK)
            else:
                path_system, path_preview, path_src, tittle = ba.download_video(data_attribute.data_attribute,
                                                                                data_attribute.type,
                                                                                data_attribute.source,
                                                                                learning_object.path_adapted, request)

                if path_system is None and path_preview is None:
                    return Response({"status": False, "code": "video_not_found",
                                     "message": "The source does not allow video download"},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    page_learning_object = tag.page_learning_object
                    file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
                    tag_adaptation = file_html.find(tag.tag, tag.id_class_ref)

                    print(page_learning_object)


                    uid = bsd.getUUID()
                    tag_adapted = TagAdapted.objects.create(
                        type="video",
                        id_ref=uid,
                        text=tittle,
                        path_src=path_src,
                        path_preview=path_preview,
                        path_system=path_system,
                        tag_page_learning_object=tag,
                    )

                    serializer = self.get_serializer(tag_adapted)

                    if data_attribute.source.find("youtube.") > -1:
                        transcripts, captions = ba.generate_transcript_youtube(data_attribute.data_attribute, tittle,
                                                                               learning_object.path_adapted, request)

                        print(transcripts)

                        for transcript in transcripts:
                            Transcript.objects.create(
                                src=transcript['src'],
                                type=transcript['type'],
                                srclang=transcript['srclang'],
                                label=transcript['label'],
                                source=transcript['source'],
                                path_system=transcript['path_system'],
                                tag_adapted=tag_adapted,
                            )
                        for caption in captions:
                            Transcript.objects.create(
                                src=caption['src'],
                                type=caption['type'],
                                srclang=caption['srclang'],
                                label=caption['label'],
                                source=caption['source'],
                                path_system=caption['path_system'],
                                tag_adapted=tag_adapted
                            )

                            # print(captions)
                            # print(transcripts)

                            # transform html
                        video_template = bsd.templateVideoAdaptation(path_src, "video/mp4", tittle, captions,
                                                                     transcripts, uid)

                        print(video_template)

                        tag_adaptation.replace_with(video_template)
                        bsd.generate_new_htmlFile(file_html, page_learning_object.path)

                        return Response(serializer.data, status=status.HTTP_200_OK)
                    else:
                        # transform html
                        video_template = bsd.templateVideoAdaptation(path_src, "video/mp4", tittle, captions,
                                                                     transcripts, uid)
                        tag_adaptation.replace_with(video_template)
                        bsd.generate_new_htmlFile(file_html, page_learning_object.path)

                        return Response({"data": serializer.data, "message": "The source has no translations",
                                         "code": "no_suported_transcript"}, status=status.HTTP_200_OK)


class VideoGenericAPIView(GenericAPIView):
    pass


@api_view(['GET'])
def transcript_api_view(request, pk=None):
    print(request)
    if request.method == 'GET':
        transcript = get_object_or_404(Transcript, pk=pk)

        with open(transcript.path_system, 'r') as f:
            data = json.load(f)
            return Response({"id": transcript.id, "transcript": data}, status=status.HTTP_200_OK)


""" 
@api_view(['POST'])
def paragraph_api_view(request, pk=None):
    if request.method == 'POST':
        return Response({"status": "ok"})
    pass

"""
"""
@api_view(['POST'])
def image_api_view(request, pk=None):
    if request.method == 'POST':
        return Response({"status": "ok"})
    pass

"""
"""
@api_view(['POST'])
def video_api_view(request, pk=None):
    if request.method == 'POST':
        return Response({"status": "ok"})
    pass

"""
"""
@api_view(['POST'])
def audio_api_view(request, pk=None):
    if request.method == 'POST':
        return Response({"status": "ok"})
    pass

"""
"""
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
"""


class comprimeFileZip(RetrieveAPIView):
    def get(self, request, pk):
        learning_object = LearningObject.objects.get(pk=pk)
        path_folder = os.path.join(BASE_DIR, learning_object.path_adapted)
        archivo_zip = shutil.make_archive(path_folder, "zip", path_folder)
        new_path = os.path.join(request._current_scheme_host, learning_object.path_adapted + '.zip')
        print("Creado el archivo:", new_path)
        return Response({'path': new_path, 'status': 'create zip'}, status=status.HTTP_200_OK)
