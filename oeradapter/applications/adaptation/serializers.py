from rest_framework import serializers
from ..learning_object.models import PageLearningObject, TagPageLearningObject, TagAdapted, DataAttribute
from django.db.models import Q


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields = ('id', 'text', 'html_text', 'page_learning_object')


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAttribute
        fields = '__all__'


class TagsSerializerImage(serializers.ModelSerializer):
    atributes = AttributeSerializer(many=True)

    class Meta:
        model = TagPageLearningObject
        fields = ('id', 'text', 'html_text', 'page_learning_object', 'atributes')


class TagsSerializerImageUpdate(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields = ('id', 'text', 'html_text', 'page_learning_object')


class TagAdaptedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagAdapted
        # file = serializers.FileField(source='model_method')
        fields = ('id', 'text', 'html_text', 'path_preview', 'tag_page_learning_object',)


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
