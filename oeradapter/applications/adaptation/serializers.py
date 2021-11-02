from rest_framework import serializers
from ..learning_object.models import PageLearningObject, TagPageLearningObject, TagAdapted
from django.db.models import Q


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields = ('id', 'text', 'html_text', 'page_learning_object')


class TagAdaptedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagAdapted
        #file = serializers.FileField(source='model_method')
        fields = ('id', 'text', 'html_text', 'path_preview', 'tag_page_learning_object',)
