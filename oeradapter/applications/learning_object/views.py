from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from . import serializers
import shortuuid

# Create your views here.
from .models import LearningObject


class UploadLearningObject(CreateAPIView):
    serializer_class = serializers.LearningObjectSerializer

    def create(self, request, *args, **kwargs):
        uuid = str(shortuuid.ShortUUID().random(length=8))
        file = request.FILES['file']
        file._name = file._name.split('.')[0] + "_" + uuid + "." + file._name.split('.')[1]

        # request.data['user_ref'] = "user ref"
        # request.data['path_origin'] = "user ref"
        # request.data['path_adapted'] = "user ref"

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        #print(str(file._name.split('.')[0]))

        serializer.save(user_ref="referencia", path_origin="uploads", path_adapted="uploads")

        #learning_object = serializer.validated_data
        #print("learning_object" + str(learning_object))
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
