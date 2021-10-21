from rest_framework import serializers
from ..learning_object.models import PageLearningObject, TagPageLearningObject


class TagPageLearningObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields = (
            'id',
            'tag',
            'text',
            'html_text',
            'page_oa_id',
            'id_class_ref'
        )


class PageLearningObjectSerializer(serializers.ModelSerializer):
    tags = TagPageLearningObjectSerializer(many=True)

    class Meta:
        model = PageLearningObject
        fields = (
            'id',
            'path',
            'learning_object',
            'tags'
        )