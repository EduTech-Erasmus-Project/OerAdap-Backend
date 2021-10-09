from django.contrib.postgres.fields import ArrayField
from django.db import models
from datetime import datetime
from datetime import timedelta

from .manager import LearningObjectManager
import shortuuid
import os


def directory_path(instance, filename):
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
    # file = models.FileField(upload_to=directory_path)
    file_folder = models.CharField(max_length=100, null=True)
    preview_origin = models.URLField(null=True)
    preview_adapted = models.URLField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=datetime.now() + timedelta(days=1))
    file_adapted = models.FileField(upload_to=directory_path, null=True, blank=True)

    objects = LearningObjectManager()


class AdaptationLearningObject(models.Model):
    class Meta:
        db_table = 'adaptations_learning_objects'
    method = models.CharField(max_length=10)
    areas = ArrayField(models.CharField(max_length=10, blank=True), size=6)
    learning_object = models.ForeignKey(LearningObject, on_delete=models.CASCADE)


class PageLearningObject(models.Model):
    class Meta:
        db_table = 'pages_oa'
    path = models.TextField()
    learning_object = models.ForeignKey(LearningObject, on_delete=models.CASCADE)


class TagPageLearningObject(models.Model):
    class Meta:
        db_table = 'data_tag'

    tag = models.CharField(max_length=20)
    text = models.TextField(null=True)
    html_text = models.TextField(null=True)
    page_oa_id = models.ForeignKey(PageLearningObject, on_delete=models.CASCADE)
    id_class_ref = models.CharField(max_length=20)

class DataAtribute(models.Model):
    class Meta:
        db_table = 'data_atribute'
    atribute = models.CharField(max_length=100)
    data_atribute = models.CharField(max_length=100)
    data_tag = models.ForeignKey(TagPageLearningObject, on_delete=models.CASCADE)
