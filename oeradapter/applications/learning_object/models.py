from django.contrib.postgres.fields import ArrayField
from django.db import models
from datetime import datetime
from datetime import timedelta

from pytz import utc

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
    created_at = models.DateTimeField(default=datetime.now().replace(tzinfo=utc))
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=(datetime.now() + timedelta(days=1)).replace(tzinfo=utc))
    file_adapted = models.URLField(null=True)

    objects = LearningObjectManager()


class AdaptationLearningObject(models.Model):
    class Meta:
        db_table = 'adaptations_learning_objects'

    method = models.CharField(max_length=10)
    areas = ArrayField(models.CharField(max_length=10, blank=True), size=6)
    learning_object = models.ForeignKey(LearningObject, related_name="adaptation_learning_object", on_delete=models.CASCADE)


class PageLearningObject(models.Model):
    class Meta:
        db_table = 'page_learning_object'

    type = models.CharField(max_length=10, null=True)
    path = models.TextField()
    title = models.CharField(max_length=200, null=True)
    preview_path = models.URLField(null=True)
    learning_object = models.ForeignKey(LearningObject, related_name="page_learning_object", on_delete=models.CASCADE)


class TagPageLearningObject(models.Model):
    class Meta:
        db_table = 'tag_page_learning_object'

    tag = models.CharField(max_length=20)
    text = models.TextField(null=True, blank=True)
    html_text = models.TextField(null=True, blank=True)
    id_class_ref = models.CharField(max_length=20)
    page_learning_object = models.ForeignKey(PageLearningObject, related_name="tag_page_learning_object", on_delete=models.CASCADE)


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
    button_text_id = models.CharField(max_length=20, null=True)
    button_audio_id = models.CharField(max_length=20, null=True)
    tag_page_learning_object = models.OneToOneField(
        TagPageLearningObject,
        related_name="tags_adapted",
        on_delete=models.CASCADE,
        null=True
    )


class Transcript(models.Model):
    class Meta:
        db_table = "transcript"
    src = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=20, null=True, blank=True)
    srclang = models.CharField(max_length=20, null=True, blank=True)
    label = models.CharField(max_length=20, null=True, blank=True)
    source = models.CharField(max_length=20, null=True, blank=True)
    path_system = models.TextField(null=True, blank=True)
    path_preview = models.TextField(null=True, blank=True)
    tag_adapted = models.ForeignKey(
        TagAdapted,
        related_name="transcript",
        on_delete=models.CASCADE,
        null=True
    )


class DataAttribute(models.Model):
    class Meta:
        db_table = 'data_attribute'
    attribute = models.CharField(max_length=100)
    data_attribute = models.TextField()
    type = models.CharField(max_length=50, null=True, blank=True)
    path_system = models.TextField(null=True, blank=True)
    path_preview = models.URLField(max_length=255, null=True)
    source = models.CharField(max_length=20, null=True)
    tag_page_learning_object = models.ForeignKey(TagPageLearningObject, related_name="attributes",  on_delete=models.CASCADE)

class MetadataInfo(models.Model):
    class Meta:
        db_table = 'metadata_info'
    browser = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    text_number = models.CharField(max_length=100, null=True, blank=True)
    video_number = models.CharField(max_length=100, null=True, blank=True)
    audio_number = models.CharField(max_length=100, null=True, blank=True)
    img_number = models.CharField(max_length=100, null=True, blank=True)
