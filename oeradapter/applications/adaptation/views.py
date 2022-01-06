from django.db.models import Prefetch
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pyparsing import unicode
from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, GenericAPIView
from rest_framework.decorators import api_view
from unipath import Path
from . import serializers
from .serializers import TagAdaptedSerializer, PagesDetailSerializer, TagsVideoSerializer, TagAdaptedVideoSerializer, \
    TagAdaptedAudioSerializer, TagAdaptedSerializerNew, LearningObjectSerializerAdaptation
from ..learning_object.models import TagPageLearningObject, TagAdapted, PageLearningObject, LearningObject, \
    DataAttribute, Transcript, MetadataInfo
from django.db.models import Q
import os
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from ..helpers_functions import beautiful_soup_data as bsd
from ..helpers_functions import base_adaptation as ba
import shutil
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup

# Conversion de audio a texto

BASE_DIR = Path(__file__).ancestor(3)

PROD = None
with open(os.path.join(Path(__file__).ancestor(4), "prod.json")) as f:
    PROD = json.loads(f.read())


class ParagraphView(RetrieveAPIView):
    # serializer_class = serializers.TagLearningObjectDetailSerializerP
    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & (Q(tag='p') | Q(tag='span')))
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

        adapted_serializer = TagAdaptedSerializer(tag_adapted_learning_object, data=request.data)
        if adapted_serializer.is_valid():
            if str(request.data['method']) == 'img-alt':
                """Validacion de envio de datos, para realizar la actualizacion """
                if ((not request.data['text'].isspace()) & (request.data['text'] != "")):
                    """ Guardar en la base de datos"""
                    text_update = request.data['text'];
                    alt_db_aux = bsd.convertElementBeautifulSoup(str(tag_adapted_learning_object.html_text))
                    alt_db_aux = alt_db_aux.img
                    alt_db_aux['alt'] = text_update
                    tag_adapted_learning_object.html_text = str(alt_db_aux)

                    html_img_code[0]['alt'] = text_update;

            elif str(request.data['method']) == 'transform-table':
                html_change = BeautifulSoup(str(request.data['text_table']), 'html.parser')
                html_change_border = html_change.find_all('table')
                html_change_border[0]['border'] = '1'

                html_img_code[0].replace_with(html_change)

            elif str(request.data['method'] == 'update-table'):
                html_change = BeautifulSoup(str(request.data['text_table']), 'html.parser')
                table_update = file_html.find_all('figure', class_="table")
                table_update[0].replace_with(html_change)

            """Revisar si el elemento ya esta envuelto por el elemto figure"""
            """
                if html_img_code[0].parent.name != 'figure':
                    replace_html_code = bsd.templateAdaptionImage(html_img_code, tag_learning_object.id_class_ref)
                    html_img_code[0].replace_with(replace_html_code)
                else:
                    replace_description = bsd.convertElementBeautifulSoup('<em>' + text_update + "</em>")
                    html_img_code[0].parent.em.replace_with(replace_description.em)"""

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
        tag_learning_object = TagPageLearningObject.objects.get(pk=pk)
        page_learning_object = PageLearningObject.objects.get(pk=tag_learning_object.page_learning_object_id)
        audioSerializer = TagAdaptedSerializerNew(data=request.data)

        """Web Scraping"""
        div_soup_data, id_ref = bsd.templateAdaptationTag(tag_learning_object.id_class_ref)
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find('audio', tag_learning_object.id_class_ref)
        # tag['pTooltip']= 'Ver descripción visual de audio'

        tag_aux = str(tag)
        tag.insert(1, div_soup_data)

        if str(request.data['method']) == 'create':
            if ((not request.data['text'].isspace()) & (request.data['text'] != "")):
                """Serializamos los datos para guardarlos en la base de datos"""

                if audioSerializer.is_valid():
                    audioSerializer.save()

                    button_text_data = bsd.templateAudioTextButton(
                        tag_learning_object.id_class_ref,
                        request.data['text'], page_learning_object.dir_len)
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
                serializer = TagAdaptedSerializerNew(TagAdapted_create)

                button_text_data = bsd.templateAudioTextButton(
                    tag_learning_object.id_class_ref,
                    new_text, page_learning_object.dir_len)
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
        ref_change = file_html.find_all('div', id=str(tag_class_ref))
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
        print("pk search" + str(pk))
        tag_adapted = get_object_or_404(TagAdapted, tag_page_learning_object_id=pk)
        serializer = TagAdaptedAudioSerializer(tag_adapted)
        print(serializer.data)
        return Response(serializer.data)

    def post(self, request, pk=None):
        print("pk " + str(pk))
        tag_page_learning_object = get_object_or_404(TagPageLearningObject, pk=pk)

        print("tag_page_learning_object ", tag_page_learning_object)

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
                        request.data['text'], page_learning_object.dir_len)
                    tag_text = tag_adaptation.find('div', class_="tooltip text-container")
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
                    tag_page_learning_object.id_class_ref, path_src, page_learning_object.dir_len)

                tag_audio = tag_adaptation.find('div', class_="tooltip audio-container")
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
            tag = file_html.find(tag_page_learning_object.tag, tag_page_learning_object.id_class_ref)
            tag.append(div_soup_data)

            if 'text' in request.data:
                if request.data['text'] != '':
                    button_text_data, button_text_tag_id = bsd.templateAdaptedTextButton(
                        tag_page_learning_object.id_class_ref,
                        request.data['text'], page_learning_object.dir_len)
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
                    tag_page_learning_object.id_class_ref, path_src, page_learning_object.dir_len)
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
                tag_page_learning_object.id_class_ref, path_src, page_learning_object.dir_len)
            div_soup_data = tag.find(id=id_ref)
            div_soup_data.insert(len(div_soup_data) - 1, button_audio_data)

            data = TagAdapted.objects.create(
                type="p",
                id_ref=id_ref,
                path_src=path_src,
                path_preview=path_preview,
                path_system=path_system,
                tag_page_learning_object=tag_page_learning_object
            )
            serializers = self.get_serializer(data)
        else:
            tag_adaptation = file_html.find(id=tag_adapted.id_ref)
            button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
                tag_page_learning_object.id_class_ref, path_src, page_learning_object.dir_len)

            tag_audio = tag_adaptation.find('div', class_="tooltip audio-container")
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


def save_data_attribute(data_attribute, path_src, path_system, path_preview):
    data_attribute.source = "local"
    data_attribute.data_attribute = path_src
    data_attribute.path_system = path_system
    data_attribute.path_preview = path_preview
    data_attribute.save()


def save_transcript(transcript, tag_adapted):
    Transcript.objects.create(
        src=transcript['src'],
        type=transcript['type'],
        srclang=transcript['srclang'],
        label=transcript['label'],
        source=transcript['source'],
        path_system=transcript['path_system'],
        tag_adapted=tag_adapted,
    )


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

            # generar subtititulos automaticamente
            print("tag true adapted ", tag_adapted)
            print("subtitle", subtitle)

            sub_en = any(sub.srclang == "en" for sub in subtitle)
            sub_es = any(sub.srclang == "es" for sub in subtitle)

            print('sub_en', sub_en)

            if not sub_en:
                pass
            if not sub_es:
                pass

            serializer = TagsVideoSerializer(tag)

            return Response(
                {"data": serializer.data, "message": "Local translations under development", "code": "developing"},
                status=status.HTTP_200_OK)
        except:
            # learning_object = tag_adapted.objects.get(tag_page_learning_object__page_learning_object=)
            data_attribute = DataAttribute.objects.get(tag_page_learning_object_id=tag.id)
            learning_object = LearningObject.objects.get(pk=tag.page_learning_object.learning_object_id)
            print("path false ", learning_object.path_adapted)

            if data_attribute.source == "local":
                # generar subtititulos automaticamente
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

                    if data_attribute.source.find("youtube") > -1:

                        transcripts, captions = ba.generate_transcript_youtube(data_attribute.data_attribute, tittle,
                                                                               learning_object.path_adapted, request)
                        print("transcripts", transcripts)
                        print("captions", captions)

                        for transcript in transcripts:
                            save_transcript(transcript, tag_adapted)

                        for caption in captions:
                            save_transcript(caption, tag_adapted)

                            # transform html
                        video_template = bsd.templateVideoAdaptation(path_src, "video/mp4", tittle, captions,
                                                                     transcripts, uid)

                        tag_adaptation.replace_with(video_template)
                        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
                        serializer = TagsVideoSerializer(tag)

                        save_data_attribute(data_attribute, path_src, path_system, path_preview)

                        if len(transcripts) > 0 and len(captions) > 0:
                            return Response({"data": serializer.data, "message": "Transcripts downloaded",
                                             "code": "successes"}, status=status.HTTP_200_OK)
                        else:
                            return Response({"data": serializer.data, "message": "The source has no translations",
                                             "code": "no_supported_transcript"}, status=status.HTTP_200_OK)

                    else:
                        # transform html

                        save_data_attribute(data_attribute, path_src, path_system, path_preview)

                        video_template = bsd.templateVideoAdaptation(path_src, "video/mp4", tittle, captions,
                                                                     transcripts, uid)
                        tag_adaptation.replace_with(video_template)
                        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
                        serializer = TagsVideoSerializer(tag)
                        return Response({"data": serializer.data, "message": "The source has no translations",
                                         "code": "no_suported_transcript"}, status=status.HTTP_200_OK)


class VideoAddCreateAPIView(CreateAPIView):
    serializer_class = TagAdaptedVideoSerializer

    def post(self, request, pk=None):

        tag = get_object_or_404(TagPageLearningObject, pk=pk)
        page_learning_object = tag.page_learning_object
        learning_object = page_learning_object.learning_object
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)

        codes = request.data.getlist('code')
        languages = request.data.getlist('language')
        files = request.FILES.getlist('file')

        transcripts = []
        captions = []

        try:
            tag_adapted = TagAdapted.objects.get(tag_page_learning_object_id=tag.id, type="video")
            idx = 0
            for data in codes:
                subtitles = Transcript.objects.filter(tag_adapted_id=tag_adapted.id, srclang=data)
                if len(subtitles) > 0:
                    transcript, caption = save_files(learning_object, files[idx], codes[idx], languages[idx])
                    json = subtitles.get(type="JSONcc")
                    vtt = subtitles.get(type="text/vtt")
                    update_data(json, caption)
                    update_data(vtt, transcript)
                else:
                    create_transcription(files[idx], learning_object, tag_adapted, request,
                                         transcripts, captions, codes[idx], languages[idx])
                idx = idx + 1

            subtitles = Transcript.objects.filter(tag_adapted_id=tag_adapted.id)
            transcripts = []
            captions = []
            for subtitle in subtitles:
                if subtitle.type == "JSONcc":
                    transcripts.append(subtitle.__dict__)
                if subtitle.type == "text/vtt":
                    captions.append(subtitle.__dict__)

            video_template = bsd.templateVideoAdaptation(tag_adapted.path_src, "video/mp4", tag_adapted.text,
                                                         captions,
                                                         transcripts, tag_adapted.id_ref)

            tag_adaptation = file_html.find("div", tag_adapted.id_ref)
            tag_adaptation.replace_with(video_template)
            print(tag_adaptation)
            bsd.generate_new_htmlFile(file_html, page_learning_object.path)

            serializer = self.get_serializer(tag_adapted)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            data_attribute = DataAttribute.objects.get(tag_page_learning_object_id=tag.id)
            print("Create file")
            if data_attribute.source == "local":
                tag_adaptation = file_html.find(tag.tag, tag.id_class_ref)
                transcripts = []
                captions = []
                idx = 0
                uid = bsd.getUUID()
                tag_adapted = TagAdapted.objects.create(
                    type="video",
                    id_ref=uid,
                    text=data_attribute.data_attribute.split(".")[-2],
                    path_src=data_attribute.data_attribute,
                    path_preview=data_attribute.path_preview,
                    path_system=data_attribute.path_system,
                    tag_page_learning_object=tag,
                )

                serializer = self.get_serializer(tag_adapted)
                idx = 0
                for file in files:
                    transcripts, captions = create_transcription(file, learning_object, tag_adapted, request,
                                                                 transcripts,
                                                                 captions, codes[idx], languages[idx])
                    idx = idx + 1
                # path_json = ba.convert_str_to_json(path_test_str, learning_object.path_adapted, file.name)
                video_template = bsd.templateVideoAdaptation(tag_adapted.path_src, "video/mp4", tag_adapted.text,
                                                             captions,
                                                             transcripts, uid)

                print(video_template)

                tag_adaptation.replace_with(video_template)
                bsd.generate_new_htmlFile(file_html, page_learning_object.path)

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                pass
            # return Response({"status": "no adapted"}, status=status.HTTP_200_OK)


def create_transcription(file, learning_object, tag_adapted, request, transcripts, captions, language_code, language):
    # for file in files:
    transcript, caption = save_files(learning_object, file, language_code, language)

    transcripts.append(transcript)
    captions.append(caption)

    Transcript.objects.create(
        src=transcript['src'],
        type=transcript['type'],
        srclang=transcript['srclang'],
        label=transcript['label'],
        source=transcript['source'],
        path_system=transcript['path_system'],
        tag_adapted=tag_adapted,
    )
    Transcript.objects.create(
        src=caption['src'],
        type=caption['type'],
        srclang=caption['srclang'],
        label=caption['label'],
        source=caption['source'],
        path_system=caption['path_system'],
        tag_adapted=tag_adapted
    )
    # idx = idx + 1
    return transcripts, captions


def save_files(learning_object, file, code, language):
    try:
        path_srt = os.path.join(BASE_DIR, learning_object.path_adapted, "oer_resources",
                                file.name)
        ba.save_file_on_system(file, path_srt)
    except Exception as e:
        print("Error: %s ." % e)

    path_vtt = ba.convert_str_to_vtt(path_srt)
    filename = file.name
    path_json = ba.convert_str_to_json(path_srt, learning_object.path_adapted, filename.split(".")[-2])

    src = "oer_resources/" + file.name.split(".")[-2]

    transcript, caption = ba.get_object_captions_transcripts(src + ".json", src + ".vtt",
                                                             code,
                                                             language, "manual_transcription",
                                                             path_json, path_vtt)
    return transcript, caption


def update_data(subtitle, data):
    subtitle.src = data['src']
    subtitle.type = data['type']
    subtitle.srclang = data['srclang']
    subtitle.label = data['label']
    subtitle.source = data['source']
    subtitle.path_system = data['path_system']
    subtitle.save()


class VideoGenericAPIView(GenericAPIView):
    pass


@api_view(['GET'])
def transcript_api_view(request, pk=None):
    print(request)
    if request.method == 'GET':
        transcript = get_object_or_404(Transcript, pk=pk)

        with open(transcript.path_system, 'r', encoding='utf-8') as f:
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
    def get_queryset(self):
        page_learning_object = PageLearningObject.objects.all()
        return page_learning_object

    def post(self, request, pk):
        """Recibe latitud, longitud y user_agend """
        """generamos le zip del nuevo objeto de aprendizaje adaptado"""
        learning_object = LearningObject.objects.get(pk=pk)

        count_images_count, count_paragraphs_count, count_videos_count, count_audios_count = dev_count(
            learning_object.id)

        new_path = ba.compress_file(request, learning_object, count_images_count,
                                                     count_paragraphs_count, count_videos_count, count_audios_count)
        learning_object.file_adapted = new_path
        learning_object.save()
        return Response({'path': new_path, 'status': 'create zip'}, status=status.HTTP_200_OK)


def dev_count(id):
    count_images_count = 0
    count_paragraphs_count = 0
    count_videos_count = 0
    count_audios_count = 0

    tag_Adapted = TagAdapted.objects.filter(tag_page_learning_object__page_learning_object__learning_object_id=id)
    for tag in tag_Adapted:
        if str(tag.type) == 'img':
            count_images_count += 1
        if str(tag.type) == 'audio':
            count_audios_count += 1
        if str(tag.type) == 'p':
            count_paragraphs_count += 1
        if (str(tag.type) == 'video') or (str(tag.type) == 'iframe'):
            count_videos_count += 1

    return count_images_count, count_paragraphs_count, count_videos_count, count_audios_count


class returnObjectsAdapted(RetrieveAPIView):
    def get(self, request, pk):
        count_images_count, count_paragraphs_count, count_videos_count, count_audios_count = dev_count(pk)
        tag_objects = {
            'images': count_images_count,
            'audios': count_audios_count,
            'videos': count_videos_count,
            'paragraphs': count_paragraphs_count,
        }
        return Response({'tag_adapted': tag_objects})
