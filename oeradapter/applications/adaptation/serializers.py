from typing import re

from rest_framework import serializers
from ..learning_object.models import PageLearningObject, TagPageLearningObject, TagAdapted, DataAttribute
from django.db.models import Q


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields = ('id', 'text', 'html_text', 'page_learning_object')


class TagsSerializerTagUpdate(serializers.ModelSerializer):
    class Meta:
        model = TagAdapted
        fields = ('id', 'text', 'html_text', 'tag_page_learning_object', 'id_ref', 'path_src')

class DataAtributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAttribute
        fields = ('id','data_attribute','attribute','path_system')

class TagsSerializerTagAdapted(serializers.ModelSerializer):
    tags_adapted = TagsSerializerTagUpdate(required=True)
    attributes = DataAtributeSerializer(many=True)
    class Meta:
        model = TagPageLearningObject
        fields = ('id','page_learning_object','html_text','id_class_ref','attributes','tags_adapted')

class TagAdaptedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagAdapted
        # file = serializers.FileField(source='model_method')
        fields = ('id', 'text', 'html_text', 'path_preview', 'tag_page_learning_object',)


class TagAdaptedSerializerAudio(serializers.ModelSerializer):
    class Meta:
        model = TagAdapted
        fields = ('id', 'text', 'html_text', 'type', 'html_text'
                  , 'path_src', 'tag_page_learning_object', 'id_ref')


class PagesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageLearningObject
        fields = ('id', 'title', 'preview_path', 'type')

    def to_representation(self, instance):
        count_images = TagPageLearningObject.objects.filter(
            Q(page_learning_object_id=instance.id) & Q(tag='img')).count()
        count_paragraphs = TagPageLearningObject.objects.filter(
            Q(page_learning_object_id=instance.id) & Q(tag='p')).count()
        count_videos = TagPageLearningObject.objects.filter(
            Q(page_learning_object_id=instance.id) & (Q(tag='iframe') | Q(tag='video'))).count()
        count_audios = TagPageLearningObject.objects.filter(
            Q(page_learning_object_id=instance.id) & Q(tag='audio')).count()

        return {
            "id": instance.id,
            "title": instance.title,
            "preview_path": instance.preview_path,
            "type": instance.type,
            "count_data": {
                "images": count_images,
                "paragraphs": count_paragraphs,
                "videos": count_videos,
                "audios": count_audios,
            }
        }


class DataAttributeSerializer(serializers.ModelSerializer):
    #attribute_tag = serializers.StringRelatedField(many=True)

    class Meta:
        model = DataAttribute
        fields = ['id', 'attribute', 'type', 'path_preview', 'source', 'tag_page_learning_object', ]


class TagsVideoSerializer(serializers.ModelSerializer):
    attributes = DataAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = TagPageLearningObject
        fields = ['id', 'text', 'html_text', 'page_learning_object', 'attributes', ]







