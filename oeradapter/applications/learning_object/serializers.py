from rest_framework import serializers
from .models import LearningObject, AdaptationLearningObject, PageLearningObject, TagPageLearningObject
from django.db.models import Q

class LearningObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningObject
        exclude = (
            'title', 'path_origin', 'path_adapted', 'user_ref', 'expires_at', 'created_at', 'updated_at',
            'file_folder',)

    def to_representation(self, instance):
        print(instance)
        return {
            "id": instance.id,
            "title": instance.title,
            "user_ref": instance.user_ref,
            "created_at": instance.created_at,
            "expires_at": instance.expires_at,
            "preview_origin": instance.preview_origin,
            "preview_adapted": instance.preview_adapted,
        }


class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageLearningObject
        fields = ('id', 'title', 'preview_path')


class AdaptationLearningObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdaptationLearningObject
        fields = ('id', 'method', 'areas')


class LearningObjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningObject
        exclude = "__all__"

    def to_representation(self, instance):
        # config_adaptability = AdaptationLearningObject.objects.get(pk=instance.id)
        pages = PageLearningObject.objects.filter(learning_object=instance.id)
        pages = PagesSerializer(pages, many=True)

        config_adaptability = AdaptationLearningObject.objects.filter(learning_object=instance.id)
        config_adaptability = AdaptationLearningObjectSerializer(config_adaptability, many=True)

        count_pages = PageLearningObject.objects.filter(learning_object=instance.id).count()
        #test = TagPageLearningObject.objects.filter(Q(page_learning_object__learning_object__id=instance.id) & Q(tag='img')).count()
        count_images = TagPageLearningObject.objects.filter(Q(page_learning_object__learning_object__id=instance.id) & Q(tag='img')).count()
        count_paragraphs = TagPageLearningObject.objects.filter(Q(page_learning_object__learning_object__id=instance.id) & Q(tag='p')).count()
        count_videos = TagPageLearningObject.objects.filter(Q(page_learning_object__learning_object__id=instance.id) & (Q(tag='iframe') | Q(tag='video'))).count()
        count_audios = TagPageLearningObject.objects.filter(Q(page_learning_object__learning_object__id=instance.id) & Q(tag='audio')).count()
        #print(test)

        return {
            "id": instance.id,
            "oa_detail": {
                "title": instance.title,
            },
            "user_ref": instance.user_ref,
            "created_at": instance.created_at,
            "expires_at": instance.expires_at,
            "preview_origin": instance.preview_origin,
            "preview_adapted": instance.preview_adapted,
            "file_detail": {
                "pages": count_pages,
                "images": count_images,
                "paragraphs": count_paragraphs,
                "videos": count_videos,
                "audios": count_audios
            },
            "config_adaptability": config_adaptability.data[0],
            "pages": pages.data,
            "file_adapted": None
        }


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
