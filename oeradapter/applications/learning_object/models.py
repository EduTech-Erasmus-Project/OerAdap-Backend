from django.contrib.postgres.fields import ArrayField
from django.db import models
from datetime import datetime
from datetime import timedelta

from .manager import LearningObjectManager
import shortuuid
import os
import random


def directory_path(instance, filename):
    uuid = str(shortuuid.ShortUUID().random(length=8))
    path = "uploads/" + filename.split('.')[0]
    return os.path.join(path, filename)


# Create your models here.
class LearningObject(models.Model):
    class Meta:
        db_table = 'learning_objects'

    title = models.CharField(max_length=100, null=True)
    path_origin = models.CharField(max_length=100)
    path_adapted = models.CharField(max_length=100)
    user_ref = models.CharField(max_length=100)
    file = models.FileField(upload_to=directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=datetime.now() + timedelta(days=1))

    objects = LearningObjectManager()


class LearningObjectAdaptation(models.Model):
    class Meta:
        db_table = 'learning_objects_adaptations'

    method = models.CharField(max_length=10)
    areas = ArrayField(models.CharField(max_length=10, blank=True), size=6)
    learning_object = models.ForeignKey(LearningObject, on_delete=models.CASCADE)
