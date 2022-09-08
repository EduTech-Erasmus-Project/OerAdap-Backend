from rest_framework import serializers
from ..learning_object.models import LearningObject, PageLearningObject, TagPageLearningObject, TagAdapted, \
    DataAttribute, Transcript
from django.db.models import Q


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields = ('id', 'text', 'html_text', 'page_learning_object')


class TagsSerializerTagUpdate(serializers.ModelSerializer):
    class Meta:
        model = TagAdapted
        fields = ('id', 'text', 'html_text', 'tag_page_learning_object', 'id_ref', 'path_src', 'text_table', 'img_fullscreen')


class DataAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAttribute
        fields = ('id', 'data_attribute', 'attribute', 'path_system')


class TagsSerializerTagAdapted(serializers.ModelSerializer):
    tags_adapted = TagsSerializerTagUpdate(required=True)
    attributes = DataAttributeSerializer(many=True)

    class Meta:
        model = TagPageLearningObject
        fields = ('id', 'page_learning_object', 'html_text', 'id_class_ref', 'attributes', 'tags_adapted', 'adaptation')


class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = ('id', 'type', 'srclang', 'label', 'source', 'path_preview')


class TagAdaptedVideoSerializer(serializers.ModelSerializer):
    transcript = TranscriptSerializer(many=True, read_only=True)

    class Meta:
        model = TagAdapted
        fields = ('id', 'text', 'html_text', 'type', 'html_text'
                  , 'path_preview', 'tag_page_learning_object', 'id_ref', 'transcript')


class TagAdaptedSerializer(serializers.ModelSerializer):
    # tags_adapted = TagAdaptedSerializerAudio(many=True, read_only=True)

    class Meta:
        model = TagAdapted
        fields = ('id', 'text', 'html_text', 'tag_page_learning_object', 'text_table')


class TagAdaptedSerializerNew(serializers.ModelSerializer):
    class Meta:
        model = TagAdapted
        fields = ('id', 'text', 'type', 'html_text', 'tag_page_learning_object', 'id_ref')


class TagAdaptedAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagAdapted
        fields = ('id', 'text', 'html_text', 'type', 'html_text'
                  , 'path_preview', 'tag_page_learning_object', 'id_ref',)


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
    # attribute_tag = serializers.StringRelatedField(many=True)

    class Meta:
        model = DataAttribute
        fields = ['id', 'attribute', 'type', 'path_preview', 'source', 'tag_page_learning_object', ]


class TagsVideoSerializer(serializers.ModelSerializer):
    attributes = DataAttributeSerializer(many=True, read_only=True)
    tags_adapted = TagAdaptedVideoSerializer(read_only=True)

    class Meta:
        model = TagPageLearningObject
        fields = ['id', 'text', 'html_text', 'page_learning_object', 'adapting', 'attributes', 'tags_adapted', ]


class LearningObjectSerializerAdaptation(serializers.ModelSerializer):
    class Meta:
        model = LearningObject
        fields = "__all__"
