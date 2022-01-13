from rest_framework.permissions import BasePermission
from .models import LearningObject


class IsPermissionToken(BasePermission):
    def has_permission(self, request, view):
        if 'HTTP_AUTHORIZATION' in request.META:
            request.object_ref = LearningObject.objects.filter(user_ref=request.META['HTTP_AUTHORIZATION'])
            return True
        else:
            request.object_ref = []
            return False
