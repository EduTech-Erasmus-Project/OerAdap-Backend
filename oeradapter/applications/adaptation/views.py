import copy
import threading
import json
from geopy import Nominatim
from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateAPIView, GenericAPIView
from rest_framework.decorators import api_view
from unipath import Path
from . import serializers
from .serializers import TagAdaptedSerializer, PagesDetailSerializer, TagsVideoSerializer, TagAdaptedVideoSerializer, \
    TagAdaptedAudioSerializer, TagAdaptedSerializerNew
from ..learning_object.models import TagPageLearningObject, TagAdapted, PageLearningObject, LearningObject, \
    DataAttribute, Transcript, MetadataInfo
from django.db.models import Q
import os
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from ..helpers_functions import beautiful_soup_data as bsd
from ..helpers_functions import base_adaptation as ba
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).ancestor(3)

PROD = None
with open(os.path.join(Path(__file__).ancestor(4), "prod.json")) as f:
    PROD = json.loads(f.read())


class ParagraphView(RetrieveAPIView):
    queryset = TagPageLearningObject.objects.all()

    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & (Q(tag='p') | Q(tag='span')))
        pages = serializers.TagsSerializer(pages, many=True)

        return Response(pages.data, status=status.HTTP_200_OK)


class ImageView(RetrieveAPIView):
    queryset = TagPageLearningObject.objects.all()

    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & Q(tag='img'))
        pages = serializers.TagsSerializerTagAdapted(pages, many=True)
        return Response(pages.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None):
        page_website_learning_object = None
        tag_website_adapted_learning_object = None

        """Consultas"""
        page_learning_object = PageLearningObject.objects.get(tag_page_learning_object__id=pk)
        tag_adapted_learning_object = TagAdapted.objects.get(tag_page_learning_object__id=pk)
        tag_class_ref = tag_adapted_learning_object.id_ref
        if page_learning_object.is_webpage:
            name_filter = page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=page_learning_object.learning_object_id)
            tag_website_adapted_learning_object = TagAdapted.objects.get(
                tag_page_learning_object__page_learning_object__id=page_website_learning_object.id,
                id_ref=tag_class_ref)

        if str(request.data['method']) == 'img-alt':
            """Validacion de envio de datos, para realizar la actualizacion """
            if (not request.data['text'].isspace()) & (request.data['text'] != ""):
                self.__update_alt_image(request, page_learning_object, tag_class_ref,
                                        tag_adapted_learning_object)

                if page_website_learning_object is not None:
                    self.__update_alt_image(request, page_website_learning_object, tag_class_ref,
                                            tag_website_adapted_learning_object)
            else:
                return Response({'message': "Campo vacío"}, status=status.HTTP_304_NOT_MODIFIED)

        elif str(request.data['method']) == 'transform-table':
            self.__create_table(request, page_learning_object, tag_class_ref,
                                tag_adapted_learning_object)

            if page_website_learning_object is not None:
                self.__create_table(request, page_website_learning_object, tag_class_ref,
                                    tag_website_adapted_learning_object)

        elif str(request.data['method'] == 'update-table'):
            self.__update_table(request, page_learning_object, tag_class_ref,
                                tag_adapted_learning_object)

            if page_website_learning_object is not None:
                self.__update_table(request, page_website_learning_object, tag_class_ref,
                                    tag_website_adapted_learning_object)

        adapted_serializer = TagAdaptedSerializer(tag_adapted_learning_object)
        return Response(adapted_serializer.data)
        # return Response({'message': adapted_serializer.error_messages}, status=status.HTTP_304_NOT_MODIFIED)

    def __update_alt_image(self, request, page_learning_object, tag_class_ref, tag_adapted_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        text_update = request.data['text']

        if tag_adapted_learning_object.img_fullscreen:
            html_img_code = file_html.find('a', {"id": tag_class_ref})
            html_img_code["title"] = text_update
            html_img_code.findChild("img")["alt"] = text_update
        else:
            html_img_code = file_html.find("img", class_=tag_class_ref)
            html_img_code['alt'] = text_update

        tag_adapted_learning_object.html_text = str(html_img_code)
        tag_adapted_learning_object.save()

        """Revisar si el elemento ya esta envuelto por el elemto figure"""
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)

    def __create_table(self, request, page_learning_object, tag_class_ref, tag_adapted_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        html_change = BeautifulSoup(str(request.data['text_table']), 'html.parser').find("figure")
        html_change["id"] = tag_class_ref
        html_change.findChild("table")["border"] = '1'

        if tag_adapted_learning_object.img_fullscreen:
            html_img_code = file_html.find('a', {"id": tag_class_ref})
        else:
            html_img_code = file_html.find("img", class_=tag_class_ref)

        html_img_code.replace_with(copy.copy(html_change))
        tag_adapted_learning_object.text_table = str(copy.copy(html_change))
        tag_adapted_learning_object.save()

        """Revisar si el elemento ya esta envuelto por el elemto figure"""
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)

    def __update_table(self, request, page_learning_object, tag_class_ref, tag_adapted_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        html_change = BeautifulSoup(str(request.data['text_table']), 'html.parser').find("figure")
        html_change["id"] = tag_class_ref
        html_change.findChild("table")["border"] = '1'

        table_update = file_html.find('figure', {"id": tag_class_ref})
        table_update.replace_with(copy.copy(html_change))

        tag_adapted_learning_object.text_table = str(copy.copy(html_change))
        tag_adapted_learning_object.save()

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)


class AdaptedImagePreviewRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    def put(self, request, pk=None):
        preview = request.data.get('preview')
        page_learning_object = get_object_or_404(PageLearningObject,
                                                 tag_page_learning_object__id=pk)  # PageLearningObject.objects.get(tag_page_learning_object__id=pk)
        page_website_learning_object = None
        tag_adapted_learning_object = TagAdapted.objects.get(tag_page_learning_object__id=pk)

        tag_class_ref = tag_adapted_learning_object.id_ref
        if page_learning_object.is_webpage:
            name_filter = page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=page_learning_object.learning_object_id)

        try:
            tag_adapted_learning_object = self.__update_image(tag_adapted_learning_object, preview,
                                                              page_learning_object, tag_class_ref)
            if page_website_learning_object is not None:
                self.__update_image(tag_adapted_learning_object, preview, page_website_learning_object, tag_class_ref)
        except Exception as e:
            return Response({'status': 'error', 'message': e.__str__()}, status=status.HTTP_400_BAD_REQUEST)

        adapted_serializer = TagAdaptedSerializer(tag_adapted_learning_object)
        return Response(adapted_serializer.data, status=status.HTTP_200_OK)

    def __update_image(self, tag_adapted_learning_object, preview, page_learning_object, tag_class_ref):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        html_img_code = file_html.find('img', tag_class_ref)
        tag_adapted_learning_object.img_fullscreen = preview

        if preview:
            template = bsd.templateImagePreview(tag_class_ref, html_img_code.get('src', ''),
                                                html_img_code.get('alt', ''), html_img_code)
            html_img_code.replace_with(copy.copy(template))
            tag_adapted_learning_object.html_text = str(template)
            tag_adapted_learning_object.save()

        else:
            parent = file_html.find('a', {"id": tag_class_ref})
            if parent is not None:
                parent.replace_with(copy.copy(html_img_code))
                tag_adapted_learning_object.html_text = str(html_img_code)
                tag_adapted_learning_object.save()

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return tag_adapted_learning_object


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
        pages = self.get_serializer(pages, many=True)

        return Response(pages.data)


class AudioviewCreate(RetrieveAPIView):
    def post(self, request, *args, **kwargs):

        page_website_learning_object = None

        """Consulta de datos"""
        try:
            pk = request.data['tag_page_learning_object']
            tag_learning_object = TagPageLearningObject.objects.get(pk=pk)
            page_learning_object = PageLearningObject.objects.get(pk=tag_learning_object.page_learning_object_id)
        except Exception as e:
            print("error", e)
            return Response({'message': e.__str__(), 'status': 'error'},
                            status=status.HTTP_404_NOT_FOUND)

        if page_learning_object.is_webpage:
            name_filter = page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=page_learning_object.learning_object_id)
            #print("page_website_learning_object", page_website_learning_object)

        """Web Scraping"""
        div_soup_data, id_ref = bsd.templateAdaptationTag(tag_learning_object.id_class_ref)

        if str(request.data['method']) == 'create':
            if (not request.data['text'].isspace()) & (request.data['text'] != ""):
                try:
                    data = self.__create_audio(tag_learning_object, request, copy.copy(div_soup_data), id_ref,
                                               page_learning_object)

                    if page_website_learning_object is not None:
                        self.__create_audio(tag_learning_object, request, copy.copy(div_soup_data), id_ref,
                                            page_website_learning_object, True)

                    audioSerializer = TagAdaptedSerializerNew(data)
                    return Response(audioSerializer.data, status=status.HTTP_200_OK)

                except Exception as e:
                    print("error", e)
                    return Response({'message': e.__str__(), 'status': 'error'},
                                    status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'The text is required', 'status': 'error'}, status=status.HTTP_304_NOT_MODIFIED)

        elif str(request.data['method']) == 'automatic':
            """Creamos un nuevo objeto adaptado ya que agregamos el texto ahora"""
            try:
                date = self.__automatic_audio(request, copy.copy(div_soup_data), id_ref, tag_learning_object,
                                              page_learning_object)

                if page_website_learning_object is not None:
                    self.__automatic_audio(request, copy.copy(div_soup_data), id_ref, tag_learning_object,
                                           page_website_learning_object, True)

                audioSerializer = TagAdaptedSerializerNew(date)
                return Response(audioSerializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': e.__str__(), 'status': 'error'},
                                status=status.HTTP_400_BAD_REQUEST)

    def __create_audio(self, tag_learning_object, request, div_soup_data, id_ref, page_learning_object,
                       is_webpage=False):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find('audio', tag_learning_object.id_class_ref)
        tag_aux = str(tag)
        tag.insert(1, div_soup_data)
        button_text_data = bsd.templateAudioTextButton(
            tag_learning_object.id_class_ref,
            request.data['text'], page_learning_object.dir_len)
        div_soup_data = tag.find(id=id_ref)
        div_soup_data.insert(1, button_text_data)
        tag_audio_div = bsd.templateAdaptedAudio(tag_aux, tag_learning_object.id_class_ref)
        tag_audio_div.append(div_soup_data)
        tag_container = bsd.templateContainerButtons(tag_learning_object.id_class_ref, tag_audio_div)
        tag.replace_with(copy.copy(tag_container))
        data = None
        if not is_webpage:
            data = self.__create_tag(request, request.data['text'], tag_container)

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return data

    def __automatic_audio(self, request, div_soup_data, id_ref, tag_learning_object, page_learning_object,
                          is_webpage=False):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find('audio', tag_learning_object.id_class_ref)
        tag_aux = str(tag)
        tag.insert(1, div_soup_data)
        new_text = ba.convertAudio_Text(request.data['path_system'])
        button_text_data = bsd.templateAudioTextButton(
            tag_learning_object.id_class_ref,
            new_text, page_learning_object.dir_len)
        div_soup_data = tag.find(id=id_ref)
        div_soup_data.insert(1, button_text_data)
        tag_audio_div = bsd.templateAdaptedAudio(tag_aux, tag_learning_object.id_class_ref)
        tag_audio_div.append(div_soup_data)
        tag_container = bsd.templateContainerButtons(tag_learning_object.id_class_ref, tag_audio_div)
        tag.replace_with(copy.copy(tag_container))

        data = None
        if not is_webpage:
            data = self.__create_tag(request, new_text, tag_container)

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return data

    def __create_tag(self, request, new_text, tag):
        return TagAdapted.objects.create(
            tag_page_learning_object_id=request.data['tag_page_learning_object'],
            path_system=request.data['path_system'],
            id_ref=request.data['id_ref'],
            type=request.data['type'],
            html_text=str(tag),
            path_src=request.data['path_src'],
            text=new_text
        )


class AudioView(RetrieveAPIView):
    def get(self, request, pk=None):
        pages = TagPageLearningObject.objects.filter(Q(page_learning_object_id=pk) & Q(tag='audio'))
        pages = serializers.TagsSerializerTagAdapted(pages, many=True)
        return Response(pages.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None):

        """Consultas"""
        try:
            tag_learning_object = TagPageLearningObject.objects.get(pk=pk)
            page_learning_object = PageLearningObject.objects.get(pk=tag_learning_object.page_learning_object_id)
            tag_adapted_learning_object = TagAdapted.objects.get(tag_page_learning_object=tag_learning_object.id)
        except Exception as e:
            return Response({'message': e.__str__(), 'status': 'error'},
                            status=status.HTTP_404_NOT_FOUND)

        """Web Scraping"""
        tag_class_ref = tag_adapted_learning_object.id_ref
        page_website_learning_object = None

        if page_learning_object.is_webpage:
            name_filter = page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=page_learning_object.learning_object_id)
            #print("page_website_learning_object", page_website_learning_object)

        """Validacion de envio de datos, para realizar la actualizacion """
        if (not request.data['text'].isspace()) & (request.data['text'] != ""):
            """ Guardar en la base de datos"""
            adapted_serializer = TagAdaptedSerializer(tag_adapted_learning_object, data=request.data)
            if adapted_serializer.is_valid():
                """Cambiamos el texto en el html"""
                try:
                    self.__update_text(request, tag_class_ref, page_learning_object)
                    if page_website_learning_object is not None:
                        self.__update_text(request, tag_class_ref, page_website_learning_object)

                    adapted_serializer.save()
                    return Response(adapted_serializer.data)
                except Exception as e:
                    return Response({'message': e.__str__(), 'status': 'error'},
                                    status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'The text is required', 'status': 'error'}, status=status.HTTP_304_NOT_MODIFIED)

    def __update_text(self, request, tag_class_ref, page_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        ref_change = file_html.find_all('div', id=str(tag_class_ref))
        text_adapted = request.data['text']
        onChange_ref = """textAdaptationEvent('""" + str(text_adapted) + """', '""" + tag_class_ref + """', this)"""
        ref_change[0]['onclick'] = onChange_ref
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)


class AdapterParagraphTestRetrieveAPIView(RetrieveUpdateAPIView):
    serializer_class = TagAdaptedAudioSerializer

    def get(self, request, pk=None):
        """Get tag adapted by paragraph pk"""
        tag_adapted = get_object_or_404(TagAdapted, tag_page_learning_object_id=pk)
        serializer = TagAdaptedAudioSerializer(tag_adapted)
        return Response(serializer.data)

    def post(self, request, pk=None):
        page_website_learning_object = None

        tag_page_learning_object = get_object_or_404(TagPageLearningObject, pk=pk)

        page_learning_object = PageLearningObject.objects.get(type='adapted',
                                                              pk=tag_page_learning_object.page_learning_object_id)

        #print("page_learning_object", page_learning_object)

        if page_learning_object.is_webpage:
            name_filter = page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=tag_page_learning_object.page_learning_object.learning_object_id)
            #print("page_website_learning_object", page_website_learning_object)

        try:
            tag_adapted = TagAdapted.objects.get(tag_page_learning_object_id=pk)
        except Exception as e:
            #print(type(e))
            tag_adapted = None

        if tag_adapted is not None:
            # update tag adapted
            if 'text' in request.data:
                if request.data['text'] != '':
                    self.__update_text(request, tag_adapted, tag_page_learning_object, page_learning_object)

                    if page_website_learning_object is not None:
                        self.__update_text(request, tag_adapted, tag_page_learning_object, page_website_learning_object)

                else:
                    return Response(
                        {"message": "Text is empty", "code": "error"},
                        status=status.HTTP_400_BAD_REQUEST)

            if 'file' in request.data:
                try:
                    self.__update_file(request, tag_adapted, tag_page_learning_object, page_learning_object)

                    if page_website_learning_object is not None:
                        self.__update_file(request, tag_adapted, tag_page_learning_object, page_website_learning_object)

                except Exception as e:
                    return Response(
                        {"message": e.__str__(), "code": "error"},
                        status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(tag_adapted)
            return Response(serializer.data)
        else:
            div_soup_data, id_ref = bsd.templateAdaptationTag(tag_page_learning_object.id_class_ref)

            if 'text' in request.data:
                if request.data['text'] != '':

                    data = self.__create_text(request, tag_page_learning_object, id_ref, copy.copy(div_soup_data),
                                              page_learning_object)

                    if page_website_learning_object is not None:
                        self.__create_text(request, tag_page_learning_object, id_ref, copy.copy(div_soup_data),
                                           page_website_learning_object, True)

                    serializer = TagAdaptedAudioSerializer(data)
                    return Response(serializer.data)
                else:
                    return Response(
                        {"message": "Text is empty", "code": "empty_data"},
                        status=status.HTTP_400_BAD_REQUEST)

            if 'file' in request.data:
                try:
                    data = self.__create_file(request, tag_page_learning_object, id_ref, copy.copy(div_soup_data),
                                              page_learning_object)

                    if page_website_learning_object is not None:
                        self.__create_file(request, tag_page_learning_object, id_ref, copy.copy(div_soup_data),
                                           page_website_learning_object, True)

                    serializer = TagAdaptedAudioSerializer(data)
                    return Response(serializer.data)
                except Exception as e:
                    return Response(
                        {"message": e.__str__(), "code": "error"},
                        status=status.HTTP_400_BAD_REQUEST)

    def __update_text(self, request, tag_adapted, tag_page_learning_object, page_learning_object):
        #print("update page_learning_object.path", page_learning_object.path)
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find("div", id=tag_page_learning_object.id_class_ref)
        tag_adaptation = tag.find(id=tag_adapted.id_ref)

        button_text_data, button_text_tag_id = bsd.templateAdaptedTextButton(
            tag_page_learning_object.id_class_ref,
            request.data['text'], page_learning_object.dir_len)
        tag_text = tag_adaptation.find('div', class_="tooltip text-container")
        if tag_text is not None:
            tag_text.decompose()
        tag_adaptation.insert(1, button_text_data)

        tag_adapted.text = request.data['text']
        tag_adapted.html_text = str(tag)

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        tag_adapted.save()

    def __create_text(self, request, tag_page_learning_object, id_ref, div_soup_data, page_learning_object,
                      is_webpage=False):
        #print("create page_learning_object.path", page_learning_object.path)
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find(tag_page_learning_object.tag, tag_page_learning_object.id_class_ref)

        tag.append(div_soup_data)

        #print("tag", tag)

        button_text_data, button_text_tag_id = bsd.templateAdaptedTextButton(
            tag_page_learning_object.id_class_ref,
            request.data['text'], page_learning_object.dir_len)
        div_soup = tag.find(id=id_ref)
        div_soup.insert(1, button_text_data)

        #print("div_soup", div_soup)

        tag_container = bsd.templateContainerButtons(tag_page_learning_object.id_class_ref, tag)
        tag.replace_with(copy.copy(tag_container))

        data = None

        if not is_webpage:
            data = TagAdapted.objects.create(
                text=request.data['text'],
                html_text=str(tag_container),
                type="p",
                id_ref=id_ref,
                tag_page_learning_object=tag_page_learning_object
            )
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return data

    def __update_file(self, request, tag_adapted, tag_page_learning_object, page_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find("div", id=tag_page_learning_object.id_class_ref)
        tag_adaptation = tag.find(id=tag_adapted.id_ref)

        learning_object = LearningObject.objects.get(pk=page_learning_object.learning_object_id)
        if (tag_adapted.path_system != '') and (tag_adapted.path_system is not None):
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
        tag_adapted.html_text = str(tag)

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        tag_adapted.save()

    def __create_file(self, request, tag_page_learning_object, id_ref, div_soup_data, page_learning_object,
                      is_webpage=False):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find(tag_page_learning_object.tag, tag_page_learning_object.id_class_ref)
        tag.append(div_soup_data)

        learning_object = LearningObject.objects.get(pk=page_learning_object.learning_object_id)
        file = request.data['file']

        file_name = file._name.split('.')
        file._name = bsd.getUUID() + '.' + file_name[-1]

        path = os.path.join(BASE_DIR, learning_object.path_adapted, 'oer_resources')
        path_src = os.path.join('oer_resources', file.name).replace("\\", "/")

        path_preview, path_system = ba.save_uploaded_file(path, file, learning_object.path_adapted, request)

        button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
            tag_page_learning_object.id_class_ref, path_src, page_learning_object.dir_len)
        div_soup = tag.find(id=id_ref)

        div_soup.insert(len(div_soup) - 1, button_audio_data)

        tag_container = bsd.templateContainerButtons(tag_page_learning_object.id_class_ref, tag)
        tag.replace_with(copy.copy(tag_container))

        data = None

        if not is_webpage:
            data = TagAdapted.objects.create(
                type="p",
                id_ref=id_ref,
                path_src=path_src,
                path_preview=path_preview,
                path_system=path_system,
                tag_page_learning_object=tag_page_learning_object,
                html_text=str(tag_container),
            )
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return data


class PageRetrieveAPIView(RetrieveAPIView):
    serializer_class = PagesDetailSerializer
    queryset = PageLearningObject.objects.all()


class CovertTextToAudioRetrieveAPIView(RetrieveAPIView):
    serializer_class = TagAdaptedAudioSerializer

    def get(self, request, pk=None):
        tag_adapted = None
        page_website_learning_object = None

        tag_page_learning_object = TagPageLearningObject.objects.get(pk=pk)
        page_learning_object = PageLearningObject.objects.get(pk=tag_page_learning_object.page_learning_object_id)
        learning_object = LearningObject.objects.get(pk=page_learning_object.learning_object_id)

        # file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)

        path_src, path_system, path_preview = ba.convertText_Audio(tag_page_learning_object.text,
                                                                   learning_object.path_adapted,
                                                                   tag_page_learning_object.id_class_ref, request)

        if page_learning_object.is_webpage:
            name_filter = page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=page_learning_object.learning_object_id)
        try:
            tag_adapted = TagAdapted.objects.get(tag_page_learning_object_id=pk)

        except Exception as e:
            print(e)
            pass

        if tag_adapted is None:
            div_soup_data, id_ref = bsd.templateAdaptationTag(tag_page_learning_object.id_class_ref)
            data = self.__create_audio(path_src, path_system, path_preview, tag_page_learning_object,
                                       copy.copy(div_soup_data), id_ref, page_learning_object, False)

            if page_website_learning_object is not None:
                self.__create_audio(path_src, path_system, path_preview, tag_page_learning_object,
                                    copy.copy(div_soup_data), id_ref, page_website_learning_object, True)

            serializers = self.get_serializer(data)
        else:
            tag_adapted = self.__update_audio(path_src, path_system, path_preview, tag_page_learning_object,
                                              tag_adapted,
                                              page_learning_object)

            if page_website_learning_object is not None:
                self.__update_audio(path_src, path_system, path_preview, tag_page_learning_object, tag_adapted,
                                    page_website_learning_object)

            serializers = self.get_serializer(tag_adapted)

        return Response(serializers.data, status=status.HTTP_200_OK)

    def __create_audio(self, path_src, path_system, path_preview, tag_page_learning_object, div_soup_data, id_ref,
                       page_learning_object, is_webpage=False):

        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)

        tag = file_html.find(tag_page_learning_object.tag, tag_page_learning_object.id_class_ref)
        tag.append(div_soup_data)
        button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
            tag_page_learning_object.id_class_ref, path_src, page_learning_object.dir_len)
        div_soup_data = tag.find(id=id_ref)
        div_soup_data.insert(len(div_soup_data) - 1, button_audio_data)

        data = None

        if not is_webpage:
            data = TagAdapted.objects.create(
                type=tag_page_learning_object.tag,
                id_ref=id_ref,
                path_src=path_src,
                path_preview=path_preview,
                path_system=path_system,
                tag_page_learning_object=tag_page_learning_object,
                html_text=str(tag)
            )

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return data

    def __update_audio(self, path_src, path_system, path_preview, tag_page_learning_object, tag_adapted,
                       page_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find("div", id=tag_page_learning_object.id_class_ref)
        tag_adaptation = tag.find(id=tag_adapted.id_ref)
        button_audio_data, button_audio_tag_id = bsd.templateAdaptedAudioButton(
            tag_page_learning_object.id_class_ref, path_src, page_learning_object.dir_len)

        tag_audio = tag_adaptation.find('div', class_="tooltip audio-container")
        if tag_audio is not None:
            tag_audio.decompose()
        tag_adaptation.insert(len(tag_adaptation) - 1, button_audio_data)

        tag_adapted.path_src = path_src
        tag_adapted.path_preview = path_preview
        tag_adapted.path_system = path_system
        tag_adapted.html_text = str(tag)

        tag_adapted.save()

        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
        return tag_adapted


def save_data_attribute(data_attribute, path_src, path_system, path_preview):
    data_attribute.source = "local"
    data_attribute.data_attribute = path_src
    data_attribute.path_system = path_system
    data_attribute.path_preview = path_preview
    data_attribute.save()


class VideoGenerateCreateAPIView(CreateAPIView):
    serializer_class = TagAdaptedVideoSerializer

    def post(self, request, pk=None):
        # tag = TagPageLearningObject.objects.get(pk=pk)
        tag = get_object_or_404(TagPageLearningObject, pk=pk)
        serializer = TagsVideoSerializer(tag)

        tag_adapted = None
        subtitle = None

        try:
            tag_adapted = TagAdapted.objects.get(tag_page_learning_object_id=tag.id, type="video")
            subtitle = Transcript.objects.filter(tag_adapted_id=tag_adapted.id)

            sub_en = any(sub.srclang == "en" for sub in subtitle)
            sub_es = any(sub.srclang == "es" for sub in subtitle)

            if not sub_en:
                pass
            if not sub_es:
                pass

            return Response(
                {"data": serializer.data, "message": "Local translations under development", "code": "developing"},
                status=status.HTTP_200_OK)
        except Exception as e:
            tag_adapted = None
            subtitle = None

        if tag_adapted is None and subtitle is None:
            data_attribute = DataAttribute.objects.get(tag_page_learning_object_id=tag.id)
            learning_object = LearningObject.objects.get(pk=tag.page_learning_object.learning_object_id)

            #print("data_attribute", data_attribute)
            #print("learning_object", learning_object)

            if data_attribute.source == "local":
                # generar subtititulos automaticamente

                return Response({"message": "Local translations under development", "code": "developing"},
                                status=status.HTTP_200_OK)
            else:
                try:
                    th_download = threading.Thread(target=ba.download_video1,
                                                   args=[tag, data_attribute, learning_object, request])
                    th_download.start()
                    tag.adapting = True
                    tag.save()
                    return Response(
                        {"message": "Download Video in Thread", "code": "downloading", "data": serializer.data},
                        status=status.HTTP_200_OK)

                except Exception as e:
                    print(e)
                    tag.adapting = False
                    tag.save()
                    return Response(
                        {"message": "Error: " + e.__str__(), "code": "error_thread", "data": serializer.data},
                        status=status.HTTP_400_BAD_REQUEST)


class VideoAddCreateAPIView(CreateAPIView):
    serializer_class = TagAdaptedVideoSerializer

    def post(self, request, pk=None):
        # print("metodo post")
        tag = get_object_or_404(TagPageLearningObject, pk=pk)
        page_learning_object = tag.page_learning_object
        learning_object = page_learning_object.learning_object
        codes = request.data.getlist('code')
        languages = request.data.getlist('language')
        files = request.FILES.getlist('file')
        transcripts = []
        captions = []
        tag_adapted = None
        page_website_learning_object = None

        if tag.page_learning_object.is_webpage:
            name_filter = tag.page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=page_learning_object.learning_object_id)

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
            tag_adapted.html_text = str(video_template)
            tag_adapted.save()

            self.__update_template_html("div", tag_adapted.id_ref, copy.copy(video_template),
                                        page_learning_object)

            if page_website_learning_object is not None:
                self.__update_template_html("div", tag_adapted.id_ref, copy.copy(video_template),
                                            page_website_learning_object)

            serializer = self.get_serializer(tag_adapted)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error", e)
            if tag_adapted is not None:
                return Response({"status": "no adapted", "code": "error", "message": e.__str__()},
                                status=status.HTTP_400_BAD_REQUEST)

        if tag_adapted is None:
            data_attribute = DataAttribute.objects.get(tag_page_learning_object_id=tag.id)
            if data_attribute.source == "local":
                try:
                    uid = bsd.getUUID()
                    transcripts = []
                    captions = []
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
                    video_template = bsd.templateVideoAdaptation(tag_adapted.path_src, "video/mp4", tag_adapted.text,
                                                                 captions,
                                                                 transcripts, uid)
                    tag_adapted.html_text = str(video_template)
                    tag_adapted.save()
                    self.__update_template_html(tag.tag, tag.id_class_ref, copy.copy(video_template),
                                                page_learning_object)
                    if page_website_learning_object is not None:
                        self.__update_template_html(tag.tag, tag.id_class_ref, copy.copy(video_template),
                                                    page_website_learning_object)

                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Exception as e:
                    #print("error in create tag adapted", e)
                    return Response({"status": "no adapted", "code": "error", "message": e.__str__()},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                print("is local")
                return Response({"status": "no adapted", "code": "error", "message": "Automatic transcript developing"},
                                status=status.HTTP_400_BAD_REQUEST)

    def __update_template_html(self, tag, id_class_ref, video_template, page_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag_adaptation = file_html.find(tag, id_class_ref)
        tag_adaptation.replace_with(video_template)
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)


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

    #print("path_srt", path_srt)

    path_vtt = ba.convert_str_to_vtt(path_srt)
    filename = file.name
    path_save_json = os.path.join(BASE_DIR, learning_object.path_adapted, "oer_resources",
                                  filename.split(".")[-2] + ".json")
    path_json = ba.convert_str_to_json(path_srt, path_save_json)

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
    # print(request)
    if request.method == 'GET':
        transcript = get_object_or_404(Transcript, pk=pk)

        with open(transcript.path_system, 'r', encoding='utf-8') as f:
            # data = json.load(f)
            file_content = f.read()
            # print(file_content)
            f.close()
            return Response({"id": transcript.id, "transcript": file_content}, status=status.HTTP_200_OK, )


@api_view(['POST'])
def update_transcript_api_view(request, pk=None):
    if request.method == 'POST':
        transcript = get_object_or_404(Transcript, pk=pk)
        # print(request.data.get("data"))
        transcrips = Transcript.objects.filter(tag_adapted_id=transcript.tag_adapted, srclang=transcript.srclang)
        #print(len(transcrips))

        file_vtt = [t for t in transcrips if t.type == "text/vtt"][0]

        file_json = [t for t in transcrips if t.type == "JSONcc"][0]

        #print(file_json.path_system)

        with open(transcript.path_system, 'w+', encoding='utf-8') as file:
            file.write(request.data.get("data"))

        srt_file = ba.convert_vtt_to_str(transcript.path_system)
        json_system = ba.convert_str_to_json(srt_file, file_json.path_system)
        return Response({"id": transcript.id, "data": "ok"}, status=status.HTTP_200_OK, )


@api_view(['POST'])
def comprimeFileZip(request, pk=None):
    if request.method == 'POST':
        """Recibe latitud, longitud y user_agend """
        """generamos le zip del nuevo objeto de aprendizaje adaptado"""
        try:
            learning_object = LearningObject.objects.get(pk=pk)

            count_images_count, count_paragraphs_count, count_videos_count, count_audios_count = dev_count(
                learning_object.id)

            #print(request.data)

            if request.data.get('latitude') is not None and request.data.get('longitude') is not None:
                save_info_download(request, count_paragraphs_count, count_videos_count, count_audios_count,
                                   count_images_count,
                                   learning_object)

            path_zip_file = ba.compress_file(request, learning_object)
            learning_object.file_adapted = path_zip_file
            learning_object.save()
            return Response({'path': path_zip_file, 'status': 'create zip'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': e.__str__(), 'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)


def save_info_download(request, count_paragraphs_count, count_videos_count, count_audios_count, count_images_count,
                       learning_object):
    try:
        browser = str(request.data.get('browser', "Request Api"))
        laltitud = str(request.data['latitude'])
        longitud = str(request.data['longitude'])
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse(laltitud + "," + longitud)
        MetadataInfo.objects.update_or_create(id_learning=learning_object.id,
                                              defaults={
                                                  'browser': browser,
                                                  'country': str(location.raw['address']['country']),
                                                  'text_number': count_paragraphs_count,
                                                  'video_number': count_videos_count,
                                                  'audio_number': count_audios_count,
                                                  'img_number': count_images_count,
                                                  'id_learning': learning_object.id,
                                              })
    except Exception as e:
        # print(e)
        pass


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


class revertImageRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    def put(self, request, pk, *args, **kwargs):
        tag_page = get_object_or_404(TagPageLearningObject, pk=pk)
        page_learning_object = tag_page.page_learning_object
        adaptation = request.data.get('adaptation', False)
        page_website_learning_object = None

        if page_learning_object.is_webpage:
            name_filter = page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=page_learning_object.learning_object_id)

        try:
            tag_adapted_learning_object = TagAdapted.objects.get(tag_page_learning_object__id=pk)
        except:
            return Response("ok", status=status.HTTP_200_OK)

        if adaptation:
            if tag_adapted_learning_object is not None:
                if tag_adapted_learning_object.text_table is not None:
                    html_remplace = bsd.convertElementBeautifulSoup(tag_adapted_learning_object.text_table)
                else:
                    html_remplace = bsd.convertElementBeautifulSoup(tag_adapted_learning_object.html_text)
                self.__update_page(tag_page, copy.copy(html_remplace), page_learning_object)
                if page_website_learning_object is not None:
                    self.__update_page(tag_page, copy.copy(html_remplace), page_website_learning_object)

        else:
            html_remplace = bsd.convertElementBeautifulSoup(tag_page.html_text)
            self.__update_page(tag_page, copy.copy(html_remplace), page_learning_object)
            if page_website_learning_object is not None:
                #print("adapted page normal")
                self.__update_page(tag_page, copy.copy(html_remplace), page_website_learning_object)

        tag_page.adaptation = adaptation
        tag_page.save()

        # serializers.TagsSerializerTagAdapted(tag_page)
        return Response("ok", status=status.HTTP_200_OK)

    def __update_page(self, tag_page, html_remplace, page_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find('a', {"id": tag_page.id_class_ref})

        if tag is None:
            tag = file_html.find('figure', {"id": tag_page.id_class_ref})

        if tag is None:
            tag = file_html.find(tag_page.tag, tag_page.id_class_ref)

        tag.replace_with(html_remplace)
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)


class revertParagraphRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    def put(self, request, pk, *args, **kwargs):
        tag_page = get_object_or_404(TagPageLearningObject, pk=pk)
        page_learning_object = tag_page.page_learning_object
        adaptation = request.data.get('adaptation', False)
        page_website_learning_object = None

        if page_learning_object.is_webpage:
            name_filter = page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=page_learning_object.learning_object_id)

        try:
            tag_adapted_learning_object = TagAdapted.objects.get(tag_page_learning_object__id=pk)
        except:
            return Response("ok", status=status.HTTP_200_OK)

        if adaptation:
            if tag_adapted_learning_object is not None:
                html_remplace = bsd.convertElementBeautifulSoup(tag_adapted_learning_object.html_text)
                #print("html_remplace true", html_remplace)
                self.__update_page(tag_page, copy.copy(html_remplace), page_learning_object)
                if page_website_learning_object is not None:
                    self.__update_page(tag_page, copy.copy(html_remplace), page_website_learning_object)
        else:
            html_remplace = bsd.convertElementBeautifulSoup(tag_page.html_text)
            #print("html_remplace false", html_remplace)
            self.__update_page(tag_page, copy.copy(html_remplace), page_learning_object)
            if page_website_learning_object is not None:
                #print("adapted page normal")
                self.__update_page(tag_page, copy.copy(html_remplace), page_website_learning_object)

        tag_page.adaptation = adaptation
        tag_page.save()

        return Response("ok", status=status.HTTP_200_OK)

    def __update_page(self, tag_page, html_remplace, page_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find('div', {"id": tag_page.id_class_ref})
        if tag is None:
            tag = file_html.find(tag_page.tag, tag_page.id_class_ref)

        tag.replace_with(html_remplace)
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)


class revertVideoRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    def put(self, request, pk, *args, **kwargs):
        tag_page = get_object_or_404(TagPageLearningObject, pk=pk)
        page_learning_object = tag_page.page_learning_object
        adaptation = request.data.get('adaptation', False)
        page_website_learning_object = None

        if page_learning_object.is_webpage:
            name_filter = page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=page_learning_object.learning_object_id)

        try:
            tag_adapted_learning_object = TagAdapted.objects.get(tag_page_learning_object__id=pk)
        except:
            return Response("ok", status=status.HTTP_200_OK)

        if adaptation:
            if tag_adapted_learning_object is not None:
                html_remplace = bsd.convertElementBeautifulSoup(tag_adapted_learning_object.html_text)
                self.__update_page(tag_page, copy.copy(html_remplace), page_learning_object)
                if page_website_learning_object is not None:
                    self.__update_page(tag_page, copy.copy(html_remplace), page_website_learning_object)
        else:
            html_remplace = bsd.convertElementBeautifulSoup(tag_page.html_text)
            self.__update_page(tag_page, copy.copy(html_remplace), page_learning_object)
            if page_website_learning_object is not None:
                self.__update_page(tag_page, copy.copy(html_remplace), page_website_learning_object)

        tag_page.adaptation = adaptation
        tag_page.save()

        return Response("ok", status=status.HTTP_200_OK)

    def __update_page(self, tag_page, html_remplace, page_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find('div', {"id": tag_page.id_class_ref})
        if tag is None:
            tag = file_html.find(tag_page.tag, tag_page.id_class_ref)

        tag.replace_with(html_remplace)
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)


class revertAudioRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    def put(self, request, pk, *args, **kwargs):
        tag_page = get_object_or_404(TagPageLearningObject, pk=pk)
        page_learning_object = tag_page.page_learning_object
        adaptation = request.data.get('adaptation', False)
        page_website_learning_object = None

        if page_learning_object.is_webpage:
            name_filter = page_learning_object.file_name.replace('website_', '')
            page_website_learning_object = PageLearningObject.objects.get(file_name=name_filter,
                                                                          is_webpage=False,
                                                                          learning_object_id=page_learning_object.learning_object_id)

        try:
            tag_adapted_learning_object = TagAdapted.objects.get(tag_page_learning_object__id=pk)
        except:
            return Response("ok", status=status.HTTP_200_OK)

        if adaptation:
            if tag_adapted_learning_object is not None:

                html_remplace = bsd.convertElementBeautifulSoup(tag_adapted_learning_object.html_text)
                #print("html_remplace true", html_remplace)
                self.__update_page(tag_page, copy.copy(html_remplace), page_learning_object)
                if page_website_learning_object is not None:
                    self.__update_page(tag_page, copy.copy(html_remplace), page_website_learning_object)

        else:
            html_remplace = bsd.convertElementBeautifulSoup(tag_page.html_text)
            self.__update_page(tag_page, copy.copy(html_remplace), page_learning_object)
            if page_website_learning_object is not None:
                self.__update_page(tag_page, copy.copy(html_remplace), page_website_learning_object)

        tag_page.adaptation = adaptation
        tag_page.save()

        return Response("ok", status=status.HTTP_200_OK)

    def __update_page(self, tag_page, html_remplace, page_learning_object):
        file_html = bsd.generateBeautifulSoupFile(page_learning_object.path)
        tag = file_html.find('div', {"id": tag_page.id_class_ref})
        if tag is None:
            tag = file_html.find(tag_page.tag, tag_page.id_class_ref)

        tag.replace_with(html_remplace)
        bsd.generate_new_htmlFile(file_html, page_learning_object.path)
