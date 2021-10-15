from django.db.models import Prefetch
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from . import serializers
import shortuuid
import json
from zipfile import ZipFile
from os import listdir, rmdir
import shutil
import os
from unipath import Path
from bs4 import BeautifulSoup
from .models import LearningObject, AdaptationLearningObject, PageLearningObject, TagPageLearningObject, DataAtribute,directory_path
from .serializers import PageLearningObjectSerializaer, TagPageLearningObjectSerializer


BASE_DIR = Path(__file__).ancestor(3)

class UploadFileViewSet(viewsets.GenericViewSet):
    """
        File Learning Object
    """
    model = LearningObject
    serializer_class = serializers.LearningObjectSerializer

    def extract_zip_file(self, path, file_name, file):
        """
        Extrae un archivo zip en una ruta determinada
        :param path:
        :param file_name:
        :param file:
        :return:
        """
        var_name = os.path.join(path, file_name)
        if var_name.find('.zip.zip') >= 0:
            test_file_aux = file_name.split('.')[0]
            test_file_aux = test_file_aux.rstrip(".zip")
        else:
            test_file_aux = file_name.split('.')[0]

        directory_origin = os.path.join(path, file_name.split('.')[0], test_file_aux + "_origin")

        with ZipFile(file, 'r') as zip_file:
            # zip.printdir()
            zip_file.extractall(directory_origin)

        if self.check_files(directory_origin) == 0:
            aux_path_o = os.path.join(directory_origin, listdir(directory_origin)[0])
            source = aux_path_o
            destination = directory_origin
            files = os.listdir(source)
            for file in files:
                new_path = shutil.move(f"{source}/{file}", destination)
                print(new_path)
            rmdir(aux_path_o)
            print("directory_name", str(directory_origin))

        directory_adapted = os.path.join(path, file_name.split('.')[0], test_file_aux + "_adapted")
        shutil.copytree(directory_origin, directory_adapted)
        
        return directory_origin, directory_adapted

    def check_files(self, directory_name):
        """
        Chequea si un directorio
        :param directory_name:
        :return:
        """
        if len(listdir(directory_name)) > 1:
            return 1
        elif len(listdir(directory_name)) == 1:
            return 0

    def generateBeautifulSoupFile(self, html_doc):
        """
        Genera un objeto de BeautifulSoup para realizar web scraping
        :param html_doc:
        :return BeautifulSoup Data:
        """
        soup_data = None
        with open(html_doc,encoding='utf8') as file:
            soup_data = BeautifulSoup(file, "html.parser")
            file.close()
            return soup_data

    def read_html_files(self, file):
        """Lectura de archivos html
        return :
        """
        files = []
        for entry in os.scandir(file):
            if entry.path.endswith(".html"):
                # print(entry.path)
                files.append(entry.path)
        return files

    def save_filesHTML_db(self, files, learningObject,directory):
        """Lectura de archivos html,
        guardamos cada directorio
        de cada archivo en la base
        de datos
        """
        pages_convert = []

        for file in files:
            Page = PageLearningObject(path=file,learning_object=learningObject)
            Page.save()

            page_object = PageLearningObject.objects.get(pk=Page.id)
            #print("Objeto"+str(Page_object))
            directory_file= os.path.join(BASE_DIR, directory, file)
            soup_data = self.generateBeautifulSoupFile(directory_file)
            pages_convert.append(soup_data)
            newPage_html_generate = self.webScraping_P(soup_data, page_object)

            self.generate_new_htmlFile(newPage_html_generate,file )

    def webScraping_P(self, aux_text, page_id):
        """ Exatraccion de los parrafos de cada pagina html,
        se crea un ID unico, para identificar cada elemento
        """
        # print(aux_text)
        tag_identify = "p"
        class_name = " "
        for p_text in aux_text.find_all(tag_identify):
            if (p_text.string):
                if (len(p_text.string) >= 20):

                    if (p_text.get('class', [])):
                        class_name = p_text['class']
                    else:
                        uuid = str(shortuuid.ShortUUID().random(length=8))
                        var_uuid = tag_identify+'-' + uuid
                        p_text['class'] = var_uuid
                        class_name = var_uuid
                    Paragraph =  TagPageLearningObject(tag=tag_identify, text = str(p_text.string),
                                 html_text=str(p_text),page_oa_id= page_id, id_class_ref = class_name)
                    Paragraph.save()
            elif not p_text.string:
                print("Parrafo vacio")

        """Vamos a extraer el alt de las imagenes y crear clases en las imagenes"""
        tag_identify_img = "img"
        class_name_img = " "
        atribute_img = "src"
        text_alt = " "
        for img_text in aux_text.find_all(tag_identify_img):
            # print(  p_text['alt'] )
            # print(p_text.get('alt', []).isspace(),"\n")
            if (img_text.get('class', [])):
                class_name_img = img_text['class']
            else:
                uuid = str(shortuuid.ShortUUID().random(length=8))
                class_name_img= tag_identify_img+'-' + uuid
                img_text['class'] = class_name_img

            if (img_text.get('alt', [])):
                if (img_text.get('alt', []).isspace() == False):
                    text_alt = img_text.get('alt', [])
                else:
                    #print("No tiene texto", "\n")
                    text_alt = None
            else:
                # p_text['class'] = 'p-'+uuid
                #print("No tiene alt", "\n")
                text_alt = None

            Image_details = TagPageLearningObject(
                tag=tag_identify_img, text=str(text_alt),
                html_text=str(img_text), page_oa_id=page_id, id_class_ref=class_name_img
            )
            Image_details.save()

            Tag_page_object = TagPageLearningObject.objects.get(pk=Image_details.id)

            Image_directory = DataAtribute(
                atribute=atribute_img,
                data_atribute=str(img_text.get('src', [])),
                data_tag_id=Tag_page_object
            )
            Image_directory.save()

        return aux_text

    def generate_new_htmlFile(self,aux_text, directorio_Raiz):
        html = aux_text.prettify('utf-8')
        print("utf:", html)
        new_direction = directorio_Raiz
        if os.path.exists(new_direction):
            with open(new_direction , "wb") as file:
                file.write(html)
        else:
            os.mkdir(new_direction)
            with open(new_direction, "wb") as file:
                file.write(html)

    def get_queryset(self):
        user_token = None
        try:
            user_token = self.request.COOKIES['user_ref']
        except:
            return []
        if user_token is not None:
            return self.get_serializer().Meta.model.objects.filter(user_ref=user_token)

    def list(self, request):
        data = self.get_queryset()
        data = self.get_serializer(data, many=True)
        return Response(data.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
            Upload file attribute required file
            file > type file
            Return
            "id"
            "title"
            "user_ref"
            "created_at"
            "expires_at"
        """
        user_token = None
        try:
            user_token = request.COOKIES['user_ref']
        except:
            user_token = str(shortuuid.ShortUUID().random(length=64))

        uuid = str(shortuuid.ShortUUID().random(length=8))
        file = request.FILES['file']
        file._name = file._name.split('.')[0] + "_" + uuid + "." + file._name.split('.')[1]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract file
        path = "uploads"
        file_name = file._name
        directory_origin, directory_adapted = self.extract_zip_file(path, file_name, file)

        # save the learning object preview path
        preview_origin = os.path.join(request._current_scheme_host, directory_origin, 'index.html').replace("\\", "/")
        preview_adapted = os.path.join(request._current_scheme_host, directory_adapted, 'index.html').replace("\\", "/")
       #print('path'+os.path.join(BASE_DIR, directory_origin))
        soup_data = self.generateBeautifulSoupFile(os.path.join(BASE_DIR, directory_origin, 'index.html'))


        serializer.save(
            title=soup_data.find('title').text,
            path_origin=directory_origin,
            path_adapted=directory_adapted,
            user_ref=user_token,
            preview_origin=preview_origin,
            preview_adapted=preview_adapted,
            file_folder=os.path.join(path, file_name.split('.')[0])
        )


        learning_object = LearningObject.objects.get(pk=serializer.data['id'])
        files = self.read_html_files(os.path.join(BASE_DIR, directory_adapted))

        self.save_filesHTML_db(files,learning_object, directory_adapted)

        # remove file zip
        # path_file = os.path.join(path, file_name.split('.')[0], file_name)
        # os.remove(os.path.join(BASE_DIR, path_file))

        # Response data
        data = json.dumps(serializer.data, indent=4, sort_keys=True, default=str)
        response = HttpResponse(data, content_type='application/json')
        response.delete_cookie(key='user_ref')
        response.set_cookie('user_ref', value=user_token, expires=serializer.data['expires_at'])
        response.status_code = 201
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
        return response

class LearningObjectAdaptationSettingsViewSet(viewsets.GenericViewSet):
    model = AdaptationLearningObject
    serializer_class = serializers.LearningObjectAdaptationSettingsSerializer

    def create(self, request, *args, **kwargs):
        # print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()

        try:
            if request.data['areas'].index('image') >= 0:
                print("image in list")
            if request.data['areas'].index('video') >= 0:
                print("video in list")
            if request.data['areas'].index('audio') >= 0:
                print("audio in list")
            if request.data['areas'].index('button') >= 0:
                print("button in list")
            if request.data['areas'].index('paragraph') >= 0:
                print("paragraph in list")
        except:
            pass

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PageOAViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageLearningObject.objects.all()
    serializer_class = PageLearningObjectSerializaer
    def get_queryset(self):
        queryset= super().get_queryset()
        queryset = queryset.prefetch_related(
            Prefetch('tags')
        )
        return queryset

class TagPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TagPageLearningObject.objects.all()
    serializer_class = TagPageLearningObjectSerializer
    model = TagPageLearningObject
