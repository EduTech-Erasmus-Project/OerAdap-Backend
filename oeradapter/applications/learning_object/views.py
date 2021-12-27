import threading
from datetime import datetime

from pytz import utc
from rest_framework import status
from rest_framework.decorators import api_view
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
from .models import LearningObject, AdaptationLearningObject, PageLearningObject, TagPageLearningObject, TagAdapted, \
    RequestApi
from .permission import IsPermissionToken
from .serializers import LearningObjectSerializer, ApiLearningObjectDetailSerializer
from ..helpers_functions import beautiful_soup_data as bsd
from ..helpers_functions import base_adaptation as ba
from ..helpers_functions import automatic_adaptation as aa
from ..helpers_functions import email as email_handler
from rest_framework import generics

BASE_DIR = Path(__file__).ancestor(3)

PROD = None
with open(os.path.join(Path(__file__).ancestor(4), "prod.json")) as f:
    PROD = json.loads(f.read())


def adaptation_settings(areas, files, directory):
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


def get_learning_objects_by_token(user_ref):
    data = LearningObject.objects.filter(user_ref=user_ref)
    excludes = []
    for item in data:
        expired_on = item.expires_at.replace(tzinfo=utc)
        checked_on = datetime.now().replace(tzinfo=utc)
        # print(expired_on)
        # print(checked_on)
        if expired_on <= checked_on:
            ba.remove_folder(os.path.join(BASE_DIR, item.file_folder))
            excludes.append(item.id)
            item.delete()
    data = data.exclude(id__in=excludes)
    serializer = LearningObjectSerializer(data, many=True)
    return serializer


def create_learning_object(request, user_token, Serializer, areas, method):
    uuid = str(shortuuid.ShortUUID().random(length=8))
    file = request.FILES['file']

    file._name = file._name.split('.')[0] + "_" + uuid + "." + file._name.split('.')[1]

    # Extract file
    path = "uploads"
    file_name = file._name
    directory_origin, directory_adapted = ba.extract_zip_file(path, file_name, file)

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
    serializer = Serializer(learning_object)  # LearningObjectSerializer(learning_object)

    AdaptationLearningObject.objects.create(
        method=method,
        areas=areas,
        learning_object=learning_object
    )

    files = bsd.read_html_files(os.path.join(BASE_DIR, directory_adapted))
    adaptation_settings(areas, files, directory_adapted)
    bsd.save_filesHTML_db(files, learning_object, directory_adapted, directory_origin, request._current_scheme_host)
    return serializer, learning_object


def automatic_adaptation(areas, request, learning_object):
    paragraph_th = None
    video_th = None
    audio_th = None
    image_th = None

    if 'paragraph' in areas:
        # aa.paragraph_adaptation(learning_object, request)
        paragraph_th = threading.Thread(name="paragraph", target=aa.paragraph_adaptation,
                                        args=(learning_object, request))

    if 'audio' in areas:
        audio_th = None
        aa.audio_adaptation(learning_object, request)
    if 'image' in areas:
        image_th = None
        aa.image_adaptation(learning_object, request)
    if 'video' in areas:
        # aa.video_adaptation(learning_object, request)
        video_th = threading.Thread(name="video", target=aa.video_adaptation,
                                    args=(learning_object, request))

    if paragraph_th is not None:
        paragraph_th.start()
    if video_th is not None:
        video_th.start()

    if paragraph_th is not None:
        paragraph_th.join()
    if video_th is not None:
        video_th.join()

    # aa.adaptation(areas, files, request)
    # Response().write(self, {"state": "process"})
    # Response({"state": "process"})
    # Response({"state": "done"})
    return True


class LearningObjectCreateApiView(generics.GenericAPIView):
    """
        File Learning Object
    """
    permission_classes = [IsPermissionToken]
    serializer_class = serializers.LearningObjectSerializer

    def get_queryset(self):
        return self.get_serializer().Meta.model.objects.all

    def get(self, request, *args, **kwargs):

        if 'HTTP_AUTHORIZATION' in request.META:
            user_ref = request.META['HTTP_AUTHORIZATION']
            serializer = get_learning_objects_by_token(user_ref)
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

        # print(self.request)
        areas = request.data['areas'].split(sep=',')
        ## metodo par aguardar
        serializer, learning_object = create_learning_object(request, user_token, LearningObjectSerializer, areas,
                                                             request.data['method'])

        if request.data['method'] == "handbook":
            return Response(serializer.data)

        if request.data['method'] == "automatic" or request.data['method'] == "mixed":

            ## adaptayion method
            state = automatic_adaptation(areas, request, learning_object)
            return Response(serializer.data)

        else:
            return Response({"state": "Error method not supported"}, status=status.HTTP_400_BAD_REQUEST)


class LearningObjectRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.LearningObjectDetailSerializer

    def get_queryset(self):

        return self.get_serializer().Meta.model.objects.filter()

    def get(self, request, pk=None):
        if 'HTTP_AUTHORIZATION' in request.META:
            # print(request.META['HTTP_AUTHORIZATION'])
            # data = LearningObject.objects.filter(user_ref=request.META['HTTP_AUTHORIZATION'], pk=pk)
            data = get_object_or_404(LearningObject, pk=pk, user_ref=request.META['HTTP_AUTHORIZATION'])

            expired_on = data.expires_at.replace(tzinfo=utc)
            checked_on = datetime.now().replace(tzinfo=utc)
            if expired_on <= checked_on:
                ba.remove_folder(os.path.join(BASE_DIR, data.file_folder))
                data.delete()
                return Response({"status": False, "code": "expire_time", "message": "Time expired"},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(data)
            return Response(serializer.data)
        else:
            return Response({"status": False, "code": "ERROR_UNAUTHORIZED", "message": "no authorization key"},
                            status=status.HTTP_401_UNAUTHORIZED)


class RequestApiEmail(generics.CreateAPIView):
    """
    Envío de email de api key
    """
    serializer_class = serializers.RequestApiSerializer

    def get_queryset(self):
        return self.get_serializer().Meta.model.objects.filter()

    def post(self, request, *args, **kwargs):
        res_email = None
        try:
            api_key = shortuuid.ShortUUID().random(length=64)
            request_api = RequestApi.objects.get(email=request.data['email'])
            request_api.api_key = api_key
            res_email = email_handler.send_email_apikey(request_api.email, api_key)
            request_api.save()
        except:
            api_key = shortuuid.ShortUUID().random(length=64)
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"message": "invalid argument"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(api_key=api_key)
            res_email = email_handler.send_email_apikey(request.data['email'], api_key)

        return Response(res_email.json(), status=status.HTTP_200_OK)


@api_view(['POST'])
def email_contact_api_view(request):
    """
    Envío de email de contacto.
    :param request:
    :return Response Http:
    """
    if request.method == 'POST':
        res_email = email_handler.send_email_contact(request.data['name'], request.data['email'],
                                                     request.data['message'])
        return Response(res_email.json(), status=status.HTTP_200_OK)


@api_view(['POST'])
def api_upload(request):
    if request.method == 'POST':
        if "file" not in request.FILES:
            return Response(
                {"status": False, "message": "The zip file is required in the request.", "code": "required_file"},
                status=status.HTTP_400_BAD_REQUEST)

        if request.FILES["file"].name.split(sep='.')[-1] != "zip":
            return Response(
                {"status": False, "message": "The file is not a .zip, a file with a .zip extension is required.",
                 "code": "incorrect_format"},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            api_data = RequestApi.objects.get(api_key=request.GET.get('api_key', None))
            areas = request.GET.get('adaptation', None).split(sep=',')
            serializer, learning_object = create_learning_object(request, api_data.api_key,
                                                                 ApiLearningObjectDetailSerializer,
                                                                 areas, "automatic")
            state = automatic_adaptation(areas, request, learning_object)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("error ", e)
            return Response(
                {"status": False, "message": "The access key to the api is not valid", "code": "invalid_api_key"},
                status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def api_get_files(request):
    if request.method == 'GET':
        try:
            learning_objects = LearningObject.objects.filter(user_ref=request.GET.get('api_key', None))
            serializer = ApiLearningObjectDetailSerializer(learning_objects, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("error ", e)
            return Response(
                {"status": False, "message": "The access key to the api is not valid", "code": "invalid_api_key"},
                status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def api_get_file(request, pk=None):
    if request.method == 'GET':
        if request.GET.get('api_key', None) is None:
            return Response(
                {"status": False, "message": "The access key to the api is not valid", "code": "invalid_api_key"},
                status=status.HTTP_401_UNAUTHORIZED)
        try:
            learning_object = LearningObject.objects.get(pk=pk, user_ref=request.GET.get('api_key', None))
            serializer = ApiLearningObjectDetailSerializer(learning_object)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("error ", e)
            return Response(
                {"status": False, "message": "The file does not exist please check the file id",
                 "code": "file_not_found"},
                status=status.HTTP_404_NOT_FOUND)
