from rest_framework import serializers
from .models import LearningObject, AdaptationLearningObject, PageLearningObject, TagPageLearningObject, RequestApi, \
    TagAdapted, MetadataInfo
from django.db.models import Q
from ..helpers_functions import metadata as metadata


class LearningObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningObject
        exclude = (
            'title', 'path_origin', 'path_adapted', 'user_ref', 'expires_at', 'created_at', 'updated_at',
            'file_folder',)

    def to_representation(self, instance):
        # print(instance)
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
        fields = ('id', 'title', 'preview_path', 'type')


class AdaptationLearningObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdaptationLearningObject
        fields = ('id', 'method', 'areas')


def count_data(instance):
    count_pages = PageLearningObject.objects.filter(
        Q(learning_object=instance.id) & Q(type='adapted') & Q(is_webpage=False) &
        ~Q(file_name__contains="singlepage_index.html")).count()

    count_images = TagPageLearningObject.objects.filter(
        Q(page_learning_object__learning_object__id=instance.id) & Q(tag='img') & Q(
            page_learning_object__is_webpage=False) &
        ~Q(page_learning_object__file_name__contains="singlepage_index.html")).count()
    count_paragraphs = TagPageLearningObject.objects.filter(
        Q(page_learning_object__learning_object__id=instance.id) & (Q(tag='p') | Q(tag='span') | Q(tag='li')) & Q(
            page_learning_object__is_webpage=False) &
        ~Q(page_learning_object__file_name__contains="singlepage_index.html")).count()
    count_videos = TagPageLearningObject.objects.filter(
        Q(page_learning_object__learning_object__id=instance.id) & (Q(tag='iframe') | Q(tag='video')) & Q(
            page_learning_object__is_webpage=False) &
        ~Q(page_learning_object__file_name__contains="singlepage_index.html")).count()

    count_audios = TagPageLearningObject.objects.filter(
        Q(page_learning_object__learning_object__id=instance.id) & Q(tag='audio') & Q(
            page_learning_object__is_webpage=False) &
        ~Q(page_learning_object__file_name__contains="singlepage_index.html")).count()
    return count_pages, count_images, count_paragraphs, count_videos, count_audios


class LearningObjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningObject
        exclude = "__all__"

    def to_representation(self, instance):
        # config_adaptability = AdaptationLearningObject.objects.get(pk=instance.id)

        config_adaptability = AdaptationLearningObject.objects.get(learning_object=instance.id)
        config_adaptability = AdaptationLearningObjectSerializer(config_adaptability)

        # count data
        count_pages, count_images, count_paragraphs, count_videos, count_audios = count_data(instance)

        #print("adap", config_adaptability.data["areas"])

        data = {
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
            "config_adaptability": config_adaptability.data,
            # "pages_adapted": pages_adapted.data,
            # "pages_origin": pages_origin.data,
            "file_download": instance.file_adapted,
            "complete_adaptation": instance.complete_adaptation,
            "button_adaptation": instance.button_adaptation,
            "audio_adaptation": instance.audio_adaptation,
            "image_adaptation": instance.image_adaptation,
            "paragraph_adaptation": instance.paragraph_adaptation,
            "video_adaptation": instance.video_adaptation,
            "metadata": metadata.get_metadata(config_adaptability.data["areas"])
        }

        page_lea_ob = PageLearningObject.objects.filter(type='adapted', learning_object=instance.id)

        for page in page_lea_ob:
            tag_adap = TagPageLearningObject.objects.filter(page_learning_object_id=page.id)
            if (tag_adap):
                pass
            else:
                page.disabled = True;
                page.save();

        pages_adapted = PageLearningObject.objects.filter(
            Q(learning_object_id=instance.id) & Q(disabled=False) & Q(type='adapted'));

        pages_adapted = PagesSerializer(pages_adapted, many=True)

        data['pages_adapted'] = pages_adapted.data

        pages_origin = PageLearningObject.objects.filter(type='origin', learning_object=instance.id)

        pages_origin = PagesSerializer(pages_origin, many=True)

        data['pages_origin'] = pages_origin.data

        return data


class RequestApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestApi
        exclude = ('api_key',)


class ApiLearningObjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningObject
        exclude = "__all__"

    def to_representation(self, instance):
        # config_adaptability = AdaptationLearningObject.objects.get(pk=instance.id)

        config_adaptability = AdaptationLearningObject.objects.filter(learning_object_id=instance.id)
        config_adaptability = AdaptationLearningObjectSerializer(config_adaptability, many=True)

        count_pages, count_images, count_paragraphs, count_videos, count_audios = count_data(instance)

        # count resumen adaptation
        count_adap_images = TagAdapted.objects.filter(
            Q(tag_page_learning_object__page_learning_object__learning_object__id=instance.id) & Q(type='img')).count()
        count_adap_paragraphs = TagAdapted.objects.filter(
            Q(tag_page_learning_object__page_learning_object__learning_object__id=instance.id) & Q(type='p')).count()
        count_adap_videos = TagAdapted.objects.filter(
            Q(tag_page_learning_object__page_learning_object__learning_object__id=instance.id) & Q(
                type='video')).count()
        count_adap_audios = TagAdapted.objects.filter(
            Q(tag_page_learning_object__page_learning_object__learning_object__id=instance.id) & Q(
                type='audio')).count()

        data = {
            "id": instance.id,
            "oa_detail": {
                "title": instance.title,
            },
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
            "adapted_detail": {
                "images": count_adap_images,
                "paragraphs": count_adap_paragraphs,
                "videos": count_adap_videos,
                "audios": count_adap_audios
            },
            "config_adaptability": config_adaptability.data[0],
            "complete_adaptation": instance.complete_adaptation,
            "button_adaptation": instance.button_adaptation,
            "audio_adaptation": instance.audio_adaptation,
            "image_adaptation": instance.image_adaptation,
            "paragraph_adaptation": instance.paragraph_adaptation,
            "video_adaptation": instance.video_adaptation,
            "metadata": metadata.get_metadata(config_adaptability.data[0]["areas"]),
            "file_download": instance.file_adapted

        }
        return data


class InfoMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadataInfo
        exclude = "browser"