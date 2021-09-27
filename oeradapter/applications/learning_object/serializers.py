from rest_framework import serializers
from .models import LearningObject, LearningObjectAdaptation


class LearningObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningObject
        exclude = ('title', 'path_origin', 'path_adapted', 'user_ref', 'expires_at', 'created_at', 'updated_at')

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "title": instance.title,
            "user_ref": instance.user_ref,
            "created_at": instance.created_at,
            "expires_at": instance.expires_at
        }


class LearningObjectAdaptationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningObjectAdaptation
        fields = "__all__"
        #exclude = ("areas",)
