import os.path
import environ
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


@api_view(['POST'])
def receive_file(request):
    if request.data["file"] is None:
        return Response({"status": "error", "message": "File is required"}, status=status.HTTP_400_BAD_REQUEST)
    print(request.data)
    file_name = request.data["file"].split("/")[-1]
    path_file = os.path.join(BASE_DIR, "uploads", file_name)
    response = requests.get(request.data["file"])
    # print("response", request.data["file"].split("/")[-1])
    open(path_file, "wb").write(response.content)
    # print("file", file)

    try:
        file = open(path_file, "r")
        print("type file", type(file.read()))
        print("file", file.read())
        serializer, learning_object = create_learning_object(env("HOST_ROA"), "token_id",
                                                             LearningObjectSerializer,
                                                             ["image", "video", "audio", "button", "paragraph"],
                                                             "handbook", "uploads", file.read())

        print("serializer", serializer)
        print("learning_object", learning_object)
    except Exception as e:
        print("error", e)

    return Response(path_file, status=status.HTTP_200_OK)
