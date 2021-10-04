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
from .models import LearningObject, AdaptationLearningObject

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
        with open(html_doc) as file:
            soup_data = BeautifulSoup(file, "html.parser")
            file.close()
            return soup_data

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
