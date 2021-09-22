from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import viewsets
from . import serializers
import shortuuid
import json

# Create your views here.
from .models import LearningObject


class UploadFileViewSet(viewsets.GenericViewSet):
    """
        File Learning Object
    """
    model = LearningObject
    serializer_class = serializers.LearningObjectSerializer

    def get_queryset(self, user_token):
        return self.get_serializer().Meta.model.objects.filter(user_ref=user_token)

    def list(self, request):
        user_token = None
        try:
            user_token = request.COOKIES['user_ref']
        except:
            return Response([], status=status.HTTP_200_OK)

        if user_token is not None:
            data = self.get_queryset(user_token)
            data = self.get_serializer(data, many=True)
            return Response(data.data, status=status.HTTP_200_OK)



    def create(self, request, *args, **kwargs):
        """
            Upload file attribute required file
            file > type file
            Retun
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

        # request.data['user_ref'] = "user ref"
        # request.data['path_origin'] = "user ref"
        # request.data['path_adapted'] = "user ref"

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # self.perform_create(serializer)
        # print(str(file._name.split('.')[0]))
        # print(serializer.model.objects)

        # serializer.validated_data["user_ref"] = "user ref"

        """Descomprecion de los archivos """

        """Eliminar  zip"""

        serializer.save(title=file._name.split('.')[0], path_origin="uploads", path_adapted="uploads",
                        user_ref=user_token)

        # learning_object = serializer.validated_data
        # print("learning_object " + str(serializer.validated_data["file"]))
        # headers = self.get_success_headers(serializer.data)
        print(serializer.data['expires_at'])
        data = json.dumps(serializer.data, indent=4, sort_keys=True, default=str)
        response = HttpResponse(data, content_type='application/json')
        response.delete_cookie(key='user_ref')
        response.set_cookie('user_ref', value=user_token, expires=serializer.data['expires_at'])
        response.status_code = 201
        #return Response(serializer.data, status=status.HTTP_201_CREATED)
        return response
