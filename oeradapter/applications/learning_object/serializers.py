import self as self
from pip._internal.utils.subprocess import call_subprocess
from rest_framework import serializers
from .models import LearningObject, AdaptationLearningObject, PageLearningObject , TagPageLearningObject


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
            "expires_at": instance.expires_at,
            "preview_origin": instance.preview_origin,
            "preview_adapted": instance.preview_adapted,
        }


class LearningObjectAdaptationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdaptationLearningObject
        fields = "__all__"
        # exclude = ("areas",)


class TagPageLearningObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields=(
            'id',
            'tag',
            'text',
            'html_text',
            'page_oa_id',
            'id_class_ref'
        )

class PageLearningObjectSerializaer(serializers.ModelSerializer):
    tags = TagPageLearningObjectSerializer(many=True)
    class Meta:
        model = PageLearningObject
        fields = (
            'id',
            'path',
            'learning_object',
            'tags'
        )
