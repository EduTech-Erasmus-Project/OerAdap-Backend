from rest_framework import serializers
from .models import LearningObject

class LearningObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningObject
        fields = (
            '__all__'
        )