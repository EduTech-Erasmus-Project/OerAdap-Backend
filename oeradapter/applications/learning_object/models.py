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

    title = models.CharField(max_length=200, null=True)
    path_origin = models.TextField()
    path_adapted = models.TextField()
    user_ref = models.CharField(max_length=100)
    # file = models.FileField(upload_to=directory_path)
    file_folder = models.TextField()
    preview_origin = models.URLField(null=True)
    preview_adapted = models.URLField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=datetime.now() + timedelta(days=1))
    file_adapted = models.URLField(null=True)

    objects = LearningObjectManager()


class AdaptationLearningObject(models.Model):
    class Meta:
        db_table = 'adaptations_learning_objects'

    method = models.CharField(max_length=10)
    areas = ArrayField(models.CharField(max_length=10, blank=True), size=6)
    learning_object = models.ForeignKey(LearningObject, on_delete=models.CASCADE)


class PageLearningObject(models.Model):
    class Meta:
        db_table = 'page_learning_object'

    path = models.TextField()
    title = models.CharField(max_length=200, null=True)
    preview_path = models.URLField(null=True)
    learning_object = models.ForeignKey(LearningObject, on_delete=models.CASCADE)


class TagPageLearningObject(models.Model):
    class Meta:
        db_table = 'tag_page_learning_object'

    tag = models.CharField(max_length=20)
    text = models.TextField(null=True, blank=True)
    html_text = models.TextField(null=True, blank=True)
    id_class_ref = models.CharField(max_length=20)
    page_learning_object = models.ForeignKey(PageLearningObject, related_name='tags',on_delete=models.CASCADE)


class TagAdapted(models.Model):
    class Meta:
        db_table = 'tag_adapted'
    type = models.CharField(max_length=20)
    text = models.TextField(null=True, blank=True)
    html_text = models.TextField(null=True, blank=True)
    #html_text_inyection = models.TextField(null=True, blank=True)
    id_ref = models.CharField(max_length=20, null=True)
    path_src = models.TextField(null=True, blank=True)
    path_system = models.TextField(null=True, blank=True)
    path_preview = models.URLField(max_length=255, null=True)
    tag_page_learning_object = models.OneToOneField(
        TagPageLearningObject,
        on_delete=models.CASCADE,
        null=True
    )


class DataAttribute(models.Model):
    class Meta:
        db_table = 'data_atribute'

    atribute = models.CharField(max_length=100)
    data_atribute = models.TextField()
    type = models.CharField(max_length=50, null=True, blank=True)
    tag_page_learning_object = models.ForeignKey(TagPageLearningObject, on_delete=models.CASCADE)
