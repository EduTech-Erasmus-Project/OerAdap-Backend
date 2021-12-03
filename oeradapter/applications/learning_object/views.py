from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from . import serializers
import shortuuid
import json
from zipfile import ZipFile
from os import listdir, rmdir
import shutil
import os
from unipath import Path
from .models import LearningObject, AdaptationLearningObject, PageLearningObject, TagPageLearningObject
from .permission import IsPermissionToken
from .serializers import LearningObjectSerializer
from ..helpers_functions import beautiful_soup_data as bsd
from ..helpers_functions import base_adaptation as ba
from rest_framework import generics


BASE_DIR = Path(__file__).ancestor(3)

PROD = None
with open(os.path.join(Path(__file__).ancestor(4), "prod.json")) as f:
    PROD = json.loads(f.read())


def adaptation_settings(data, files, directory):
    areas = data['areas'].split(sep=',')
    button = False
    paragraph_script = False
    video = False
    # print(areas)
    if 'image' in areas:
        pass
    if 'video' in areas:
        video = True
        pass
    if 'audio' in areas:
        paragraph_script = True
        pass
    if 'button' in areas:
        button = True
        pass
    if 'paragraph' in areas:
        paragraph_script = True
        pass
    # pass
    ba.add_files_adaptation(files, directory, button, paragraph_script, video)


class LearningObjectCreateApiView(generics.GenericAPIView):
    """
        File Learning Object
    """
    # model = LearningObject
    permission_classes = [IsPermissionToken]
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
                # print(new_path)
            rmdir(aux_path_o)
            # print("directory_name", str(directory_origin))

        directory_adapted = os.path.join(path, file_name.split('.')[0], test_file_aux + "_adapted")
        shutil.copytree(directory_origin, directory_adapted)

        return directory_origin, directory_adapted

    def check_files(self, directory_name):
        """
        Chequea si un directorio
        :param directory_name:
        :return 1 or 0:
        """
        if len(listdir(directory_name)) > 1:
            return 1
        elif len(listdir(directory_name)) == 1:
            return 0

    def get_queryset(self):
        return self.get_serializer().Meta.model.objects.all

    def get(self, request, *args, **kwargs):

        if 'HTTP_AUTHORIZATION' in request.META:
            print(request.META['HTTP_AUTHORIZATION'])
            data = LearningObject.objects.filter(user_ref=request.META['HTTP_AUTHORIZATION'])
            serializer = LearningObjectSerializer(data, many=True)
            return Response(serializer.data)
        else:
            return Response([])




    def post(self, request, *args, **kwargs):
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

        if ('HTTP_AUTHORIZATION' in request.META) and (len(self.request.object_ref) > 0):
            user_token = request.META['HTTP_AUTHORIZATION']
        else:
            user_token = str(shortuuid.ShortUUID().random(length=64))

        print(self.request)

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

        if PROD['PROD']:
            preview_origin = preview_origin.replace("http://", "https://")
            preview_adapted = preview_adapted.replace("http://", "https://")


        soup_data = bsd.generateBeautifulSoupFile(os.path.join(BASE_DIR, directory_origin, 'index.html'))

        learning_object = LearningObject.objects.create(
            title=soup_data.find('title').text,
            path_origin=directory_origin,
            path_adapted=directory_adapted,
            user_ref=user_token,
            preview_origin=preview_origin,
            preview_adapted=preview_adapted,
            file_folder=os.path.join(path, file_name.split('.')[0])
        )
        serializer = LearningObjectSerializer(learning_object)

        AdaptationLearningObject.objects.create(
            method=request.data['method'],
            areas=request.data['areas'].split(sep=','),
            learning_object=learning_object
        )

        files = bsd.read_html_files(os.path.join(BASE_DIR, directory_adapted))
        adaptation_settings(request.data, files, directory_adapted)
        bsd.save_filesHTML_db(files, learning_object, directory_adapted, directory_origin, request._current_scheme_host)
        return Response(serializer.data)


class LearningObjectRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.LearningObjectDetailSerializer

    def get_queryset(self):

        return self.get_serializer().Meta.model.objects.filter()

    def get(self, request, pk=None):
        if 'HTTP_AUTHORIZATION' in request.META:
            #print(request.META['HTTP_AUTHORIZATION'])
            # data = LearningObject.objects.filter(user_ref=request.META['HTTP_AUTHORIZATION'], pk=pk)
            data = get_object_or_404(LearningObject, pk=pk, user_ref=request.META['HTTP_AUTHORIZATION'])
            serializer = self.get_serializer(data)
            return Response(serializer.data)
        else:
            return Response({"status":"ERROR_UNAUTHORIZED", "code":"no authorization key"}, status=status.HTTP_401_UNAUTHORIZED)