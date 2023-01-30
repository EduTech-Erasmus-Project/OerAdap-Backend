import base64
import os.path
from io import BytesIO
import environ
import shortuuid
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from unipath import Path
import requests
from ..learning_object.serializers import LearningObjectSerializer
from ..learning_object.views import create_learning_object

BASE_DIR = Path(__file__).ancestor(3)

env = environ.Env(
    PROD=(bool, False)
)
environ.Env.read_env(os.path.join(Path(__file__).ancestor(4), '.env'))


#@api_view(['POST'])
@require_POST
def receive_file(request):
    if request.data["file"] is None:
        return Response({"status": "error", "message": "File is required"}, status=status.HTTP_400_BAD_REQUEST)
    if request.data["user_key"] is None:
        return Response({"status": "error", "message": "Invalid key"}, status=status.HTTP_400_BAD_REQUEST)
    if request.data["id"] is None:
        return Response({"status": "error", "message": "Invalid id"}, status=status.HTTP_400_BAD_REQUEST)
    print(request.data)
    # request vallidate user key in repository

    uuid = str(shortuuid.ShortUUID().random(length=8))
    file_name = request.data["file"].split("/")[-1]
    file_name = file_name.split(".")[0] + "-" + uuid + "." + file_name.split(".")[1]
    path_file = os.path.join(BASE_DIR, "uploads", file_name)

    # print("response", request.data["file"].split("/")[-1])
    # print("response", response.content)
    # print("type response", type(response.content))

    # print("file", file)

    try:

        response = requests.get(request.data["file"])
        """ 
        with open(path_file, "wb") as f:
            f.write(response.content)
            # f.close()
            # file = open(path_file)
            print("path_file", path_file)
            print("file_name", file_name)
            f.close()
        """
        # with ZipFile(BytesIO(response.content)) as zip_file:
        # print("file", zip)
        # zip_file.extractall(path_ex)
        # zip_file.printdir()
        BytesIO(response.content)

        serializer, learning_object = create_learning_object(env("HOST"), request.data["user_key"],
                                                             LearningObjectSerializer,
                                                             ["image", "video", "audio", "button", "paragraph"],
                                                             "handbook", "uploads", BytesIO(response.content),
                                                             file_name, True)

        data = serializer.data
        encode = str(request.data["user_key"]).encode('ascii')
        base64_bytes = base64.b64encode(encode)

        encode_id = str(request.data["id"]).encode('ascii')
        base64_bytes_id = base64.b64encode(encode_id)

        data["oer_adap"] = env("HOST_OER") + "/adapter/" + str(learning_object.id) + "?ref=" + base64_bytes.decode(
            'ascii') + "&id=" + base64_bytes_id.decode('ascii')

        return Response({
            "id": request.data["id"],
            "user_key": request.data["user_key"],
            "data": data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print("error", e)
        return Response({
            "status": "error",
            "message": e.__str__()
        }, status=status.HTTP_400_BAD_REQUEST)
