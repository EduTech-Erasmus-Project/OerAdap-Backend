from rest_framework import serializers
from ..learning_object.models import PageLearningObject, TagPageLearningObject
from django.db.models import Q


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields = ('id', 'text', 'html_text','page_learning_object')


class TagLearningObjectDetailSerializerP(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        #fields = "__all__"

    def to_representation(self, instance):
        # config_adaptability = AdaptationLearningObject.objects.get(pk=instance.id)

        pages = TagPageLearningObject.objects.filter(Q(id=instance.id) & Q(tag='p'))
        pages = TagsSerializer(pages, many=True)

        return {
            "pages":pages.data
        }

class TagLearningObjectDetailSerializerI(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        #fields = "__all__"

    def to_representation(self, instance):
        # config_adaptability = AdaptationLearningObject.objects.get(pk=instance.id)

        pages = TagPageLearningObject.objects.filter(Q(id=instance.id) & Q(tag='img'))
        pages = TagsSerializer(pages, many=True)

        return {
            "pages":pages.data
        }

class TagLearningObjectDetailSerializerIf(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        #fields = "__all__"

    def to_representation(self, instance):
        # config_adaptability = AdaptationLearningObject.objects.get(pk=instance.id)

        pages = TagPageLearningObject.objects.filter(Q(id=instance.id) & (Q(tag='iframe') | Q(tag='video')))
        pages = TagsSerializer(pages, many=True)

        return {
            "pages":pages.data
        }

class TagLearningObjectDetailSerializerAu(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        #fields = "__all__"

    def to_representation(self, instance):
        # config_adaptability = AdaptationLearningObject.objects.get(pk=instance.id)

        pages = TagPageLearningObject.objects.filter(Q(id=instance.id) & Q(tag='audio'))
        pages = TagsSerializer(pages, many=True)

        return {
            "pages":pages.data
        }