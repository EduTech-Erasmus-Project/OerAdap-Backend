import threading
from datetime import datetime
import environ
from django.db.models import Q, Sum, Count
from pytz import utc
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from . import serializers
import shortuuid
import os
from unipath import Path
from .models import LearningObject, AdaptationLearningObject, PageLearningObject, TagPageLearningObject, TagAdapted, \
    RequestApi, MetadataInfo
from .permission import IsPermissionToken
from .serializers import LearningObjectSerializer, ApiLearningObjectDetailSerializer, LearningObjectDetailSerializer
from ..adaptation.serializers import TagsSerializerTagAdapted, TagsVideoSerializer
from ..helpers_functions import beautiful_soup_data as bsd
from ..helpers_functions import base_adaptation as ba
from ..helpers_functions import automatic_adaptation as aa
from ..helpers_functions import email as email_handler
from rest_framework import generics

BASE_DIR = Path(__file__).ancestor(3)

env = environ.Env(
    PROD=(bool, False)
)
environ.Env.read_env(os.path.join(Path(__file__).ancestor(4), '.env'))

''' 
PROD = None
with open(os.path.join(Path(__file__).ancestor(4), "prod.json")) as f:
    PROD = json.loads(f.read())
'''

def adaptation_settings(areas, files, directory, root_dirs):
    button = False
    paragraph_script = False
    video = False
    image = False
    if 'image' in areas:
        image = True

    if 'video' in areas:
        video = True

    if 'audio' in areas:
        paragraph_script = True

    if 'button' in areas:
        button = True

    if 'paragraph' in areas:
        paragraph_script = True

    ba.add_files_adaptation(files, directory, button, paragraph_script, video, image, root_dirs)


def get_learning_objects_by_token(user_ref):
    data = LearningObject.objects.filter(user_ref=user_ref)
    excludes = []
    for item in data:
        expired_on = item.expires_at.replace(tzinfo=utc)
        checked_on = datetime.now().replace(tzinfo=utc)
        if expired_on <= checked_on:
            ba.remove_folder(os.path.join(BASE_DIR, item.file_folder))
            excludes.append(item.id)
            item.delete()
    data = data.exclude(id__in=excludes)
    serializer = LearningObjectDetailSerializer(data, many=True)
    return serializer


def save_screenshot(learning_object):
    # print("page_learning_object")
    page_learning_object = PageLearningObject.objects.filter(Q(learning_object_id=learning_object.id) &
                                                             Q(file_name="website_index.html"))
    if len(page_learning_object) == 0:
        page_learning_object = PageLearningObject.objects.filter(Q(learning_object_id=learning_object.id) &
                                                                 Q(file_name="index.html"))
    # print("page_learning_object", page_learning_object)

    th_take_screenshot = threading.Thread(target=ba.take_screenshot,
                                          args=[learning_object, page_learning_object[0], ])
    th_take_screenshot.start()


def create_learning_object(request, user_token, Serializer, areas, method):
    uuid = str(shortuuid.ShortUUID().random(length=8))
    file = request.FILES['file']

    file._name = file._name.split('.')[0] + "_" + uuid + "." + file._name.split('.')[1]

    # Extract file
    path = "uploads"
    file_name = file._name
    try:
        directory_origin, directory_adapted = ba.extract_zip_file(path, file_name, file)
    except:
        return None, None, True

    # save the learning object preview path
    preview_origin = os.path.join(request._current_scheme_host, directory_origin, 'index.html').replace("\\", "/")
    preview_adapted = os.path.join(request._current_scheme_host, directory_adapted, 'index.html').replace("\\", "/")

    if env('PROD'):
        preview_origin = preview_origin.replace("http://", "https://")
        preview_adapted = preview_adapted.replace("http://", "https://")

    soup_data = bsd.generateBeautifulSoupFile(os.path.join(BASE_DIR, directory_origin, 'index.html'))

    files, root_dirs, is_adapted = bsd.read_html_files(os.path.join(BASE_DIR, directory_adapted))

    if is_adapted:
        return None, None, is_adapted

    learning_object = LearningObject.objects.create(
        title=soup_data.find('title').text,
        path_origin=directory_origin,
        path_adapted=directory_adapted,
        user_ref=user_token,
        preview_origin=preview_origin,
        preview_adapted=preview_adapted,
        file_folder=os.path.join(path, file_name.split('.')[0])
    )
    serializer = Serializer(learning_object)

    AdaptationLearningObject.objects.create(
        method=method,
        areas=areas,
        learning_object=learning_object
    )

    # files, root_dirs, is_adapted = bsd.read_html_files(os.path.join(BASE_DIR, directory_adapted))
    adaptation_settings(areas, files, directory_adapted, root_dirs)

    # print("files", files)
    files_website = [file for file in files if "website_" in file['file_name']]
    # print("files website", files_website)
    files_normal = [file for file in files if "website_" not in file['file_name']]
    # print("files normal", files_normal)

    bsd.save_filesHTML_db(files_normal, learning_object, directory_adapted, directory_origin,
                          request._current_scheme_host, files_website)
    learning_object.button_adaptation = True
    learning_object.save()

    bsd.save_metadata_in_xml(directory_adapted, areas)

    save_screenshot(learning_object)

    return serializer, learning_object, is_adapted


def dev_count(id):
    """
    Devuelve el numero de elementos adaptados

    :param entero id: el id del objeto de aprendizaje

    :variable entera count_images_count: almacena el numero de imagenes adaptadas
    :variable entera count_paragraphs_count: almacena el numero de parrafos adaptadas
    :variable entera count_videos_count: almacena el numero de videos adaptadas
    :variable entera count_audios_count: almacena el numero de audios adaptadas

    :return : enteros
    """
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


def automatic_adaptation(areas, request, learning_object):
    threads = list()
    if 'paragraph' in areas:
        aa.paragraph_adaptation(learning_object, request)
        # th = threading.Thread(name="paragraph", target=aa.paragraph_adaptation, args=(learning_object, request))
        # threads.append(th)
        # th.start()
        learning_object.paragraph_adaptation = True
        learning_object.save()
    if 'audio' in areas:
        aa.audio_adaptation(learning_object, request)
        learning_object.audio_adaptation = True
        learning_object.save()
    if 'image' in areas:
        aa.image_adaptation(learning_object, request)
        learning_object.image_adaptation = True
        learning_object.save()
    if 'video' in areas:
        aa.video_adaptation(learning_object, request)
        # th = threading.Thread(name="video", target=aa.video_adaptation, args=(learning_object, request))
        # threads.append(th)
        # th.start()
        learning_object.video_adaptation = True
        learning_object.save()

    for th in threads:
        th.join()

    count_images_count, count_paragraphs_count, count_videos_count, count_audios_count = dev_count(
        learning_object.id)

    new_path = ba.compress_file(request, learning_object, count_images_count,
                                count_paragraphs_count, count_videos_count, count_audios_count)

    learning_object.file_adapted = new_path
    learning_object.complete_adaptation = True
    learning_object.save()
    serializer = ApiLearningObjectDetailSerializer(learning_object)
    return Response(serializer.data)


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

        areas = request.data['areas'].split(sep=',')

        if len(areas) <= 0:
            return Response({"state": "Array Areas Empty", "code": "areas_empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer, learning_object, is_adapted = create_learning_object(request, user_token,
                                                                             LearningObjectSerializer,
                                                                             areas,
                                                                             request.data['method'])
        except Exception as e:
            return Response({"state": "error", "message": e.__str__()},
                            status=status.HTTP_400_BAD_REQUEST)

        if is_adapted:
            return Response({"state": "error", "code": "learning_object_odapted", "message": "Adapted"},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.data['method'] == "handbook":
            return Response(serializer.data)

        elif request.data['method'] == "automatic":

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


class MetadataInfoListAPIView(generics.ListAPIView):
    queryset = MetadataInfo.objects.all()
    serializer_class = serializers.InfoMetadataSerializer

    def get(self, request, *args, **kwargs):
        try:
            count_learning_object = self.queryset.values('id_learning').annotate(Count('id_learning')).count()
            count_audio = self.queryset.aggregate(Sum('audio_number'))
            count_image = self.queryset.aggregate(Sum('img_number'))
            count_paragraphs = self.queryset.aggregate(Sum('text_number'))
            count_video = self.queryset.aggregate(Sum('video_number'))
            countries = self.queryset.values('country').annotate(total=Count('country'))

            return Response({
                "learning_object": count_learning_object,
                "audio": count_audio["audio_number__sum"],
                "image": count_image["img_number__sum"],
                "paragraphs": count_paragraphs["text_number__sum"],
                "video": count_video["video_number__sum"],
                "countries": countries
            },
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "err"
            },
                status=status.HTTP_400_BAD_REQUEST)


class LearningObjectAudioRetrieveAPIView(generics.RetrieveAPIView):
    queryset = TagPageLearningObject.objects.all
    serializer_class = TagsSerializerTagAdapted

    def get(self, request, *args, **kwargs):
        tagPageLearningObject = TagPageLearningObject.objects.filter(
            Q(page_learning_object__learning_object_id=self.kwargs['pk']) &
            Q(tag='audio') &
            Q(page_learning_object__is_webpage=True))

        if len(tagPageLearningObject) <= 0:
            tagPageLearningObject = TagPageLearningObject.objects.filter(
                Q(page_learning_object__learning_object_id=self.kwargs['pk']) &
                Q(tag='audio') &
                Q(page_learning_object__is_webpage=False) &
                ~Q(page_learning_object__file_name__contains="singlepage_index.html"))

        response_data = self.get_serializer(tagPageLearningObject, many=True)
        return Response(response_data.data, status=status.HTTP_200_OK)


class LearningObjectImageRetrieveAPIView(generics.RetrieveAPIView):
    queryset = TagPageLearningObject.objects.all
    serializer_class = TagsSerializerTagAdapted

    def get(self, request, *args, **kwargs):
        tagPageLearningObject = TagPageLearningObject.objects.filter(
            Q(page_learning_object__learning_object_id=self.kwargs['pk']) &
            Q(tag='img') &
            Q(page_learning_object__is_webpage=True))

        if len(tagPageLearningObject) <= 0:
            tagPageLearningObject = TagPageLearningObject.objects.filter(
                Q(page_learning_object__learning_object_id=self.kwargs['pk']) &
                Q(tag='img') &
                Q(page_learning_object__is_webpage=False) &
                ~Q(page_learning_object__file_name__contains="singlepage_index.html"))

        response_data = self.get_serializer(tagPageLearningObject, many=True)
        return Response(response_data.data, status=status.HTTP_200_OK)


class LearningObjectVideoRetrieveAPIView(generics.RetrieveAPIView):
    queryset = TagPageLearningObject.objects.all
    serializer_class = TagsVideoSerializer

    def get(self, request, *args, **kwargs):
        tagPageLearningObject = TagPageLearningObject.objects.filter(
            Q(page_learning_object__learning_object_id=self.kwargs['pk']) &
            (Q(tag='iframe') | Q(tag='video')) &
            Q(page_learning_object__is_webpage=True))

        if len(tagPageLearningObject) <= 0:
            tagPageLearningObject = TagPageLearningObject.objects.filter(
                Q(page_learning_object__learning_object_id=self.kwargs['pk']) &
                (Q(tag='iframe') | Q(tag='video')) &
                Q(page_learning_object__is_webpage=False) &
                ~Q(page_learning_object__file_name__contains="singlepage_index.html"))

        response_data = self.get_serializer(tagPageLearningObject, many=True)
        return Response(response_data.data, status=status.HTTP_200_OK)


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
            serializer, learning_object, is_adapted = create_learning_object(request, api_data.api_key,
                                                                             ApiLearningObjectDetailSerializer,
                                                                             areas, "automatic")
            if is_adapted:
                return Response({"state": "learning_Object_Adapted"}, status=status.HTTP_400_BAD_REQUEST)

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
