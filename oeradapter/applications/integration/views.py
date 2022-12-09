import os.path
import environ
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from unipath import Path
import requests

from ..learning_object.serializers import LearningObjectSerializer
from ..learning_object.views import create_learning_object

from zipfile import ZipFile

BASE_DIR = Path(__file__).ancestor(3)

env = environ.Env(
    PROD=(bool, False)
)
environ.Env.read_env(os.path.join(Path(__file__).ancestor(4), '.env'))


@api_view(['POST'])
def receive_file(request):
    if request.data["file"] is None:
        return Response({"status": "error", "message": "File is required"}, status=status.HTTP_400_BAD_REQUEST)
    if request.data["user_key"] is None:
        return Response({"status": "error", "message": "Invalid key"}, status=status.HTTP_400_BAD_REQUEST)
    print(request.data)
    # request vallidate user key in repository

    file_name = request.data["file"].split("/")[-1]
    path_file = os.path.join(BASE_DIR, "uploads", file_name)

    # print("response", request.data["file"].split("/")[-1])
    # print("response", response.content)
    # print("type response", type(response.content))

    # print("file", file)

    try:
        response = requests.get(request.data["file"])
        with open(path_file, "wb") as f:
            f.write(response.content)
            # f.close()
            # file = open(path_file)
            print("path_file", path_file)
            print("file_name", file_name)

        with ZipFile(path_file, "r") as zip_file:
            # print("file", zip)
            # zip_file.extractall(path_ex)
            zip_file.printdir()

        # serializer, learning_object = create_learning_object(env("HOST_ROA"), "token_id",
        #                                                         LearningObjectSerializer,
        #                                                         ["image", "video", "audio", "button", "paragraph"],
        #                                                         "handbook", "uploads", path_file, file_name)

        # print("serializer", serializer)
        # print("learning_object", learning_object)



    except Exception as e:
        print("error", e)

    return Response(path_file, status=status.HTTP_200_OK)
