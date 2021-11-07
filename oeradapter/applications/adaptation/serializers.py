from rest_framework import serializers
from ..learning_object.models import PageLearningObject, TagPageLearningObject, TagAdapted, DataAttribute
from django.db.models import Q


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields = ('id', 'text', 'html_text','page_learning_object')


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAttribute
        fields='__all__'

class TagsSerializerImage(serializers.ModelSerializer):
    atributes = AttributeSerializer(many=True)
    class Meta:
        model = TagPageLearningObject
        fields=('id', 'text', 'html_text','page_learning_object','atributes')


class TagsSerializerImageUpdate(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields=('id', 'text', 'html_text','page_learning_object')



class TagAdaptedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagAdapted
        #file = serializers.FileField(source='model_method')
        fields = ('id', 'text', 'html_text', 'path_preview', 'tag_page_learning_object',)
