from rest_framework import serializers
from ..learning_object.models import PageLearningObject, TagPageLearningObject
from django.db.models import Q


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPageLearningObject
        fields = ('id', 'text', 'html_text','page_learning_object')




