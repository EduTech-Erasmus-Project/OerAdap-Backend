from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.db import models
import os


def directory_path(instance, filename):
    path = "uploads/" + filename.split('.')[0]
    return os.path.join(path, filename)


def one_day_hence():
    return timezone.now() + timezone.timedelta(days=1)


# Create your models here.
class LearningObject(models.Model):
    class Meta:
        db_table = 'learning_objects'

    title = models.CharField(max_length=200, null=True)
    path_origin = models.TextField()
    path_adapted = models.TextField()
    user_ref = models.CharField(max_length=100)
    file_folder = models.TextField()
    preview_origin = models.URLField(null=True)
    preview_adapted = models.URLField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=one_day_hence)
    file_adapted = models.URLField(null=True)
    complete_adaptation = models.BooleanField(default=False, null=True)
    button_adaptation = models.BooleanField(default=False, null=True)
    audio_adaptation = models.BooleanField(default=False, null=True)
    image_adaptation = models.BooleanField(default=False, null=True)
    paragraph_adaptation = models.BooleanField(default=False, null=True)
    video_adaptation = models.BooleanField(default=False, null=True)
    path_xml = models.CharField(max_length=250, null=True, blank=True)
    roa = models.BooleanField(default=False)


class AdaptationLearningObject(models.Model):
    class Meta:
        db_table = 'adaptations_learning_objects'

    method = models.CharField(max_length=10)
    areas = ArrayField(models.CharField(max_length=10, blank=True), size=6)
    learning_object = models.ForeignKey(LearningObject,
                                        related_name="adaptation_learning_object",
                                        on_delete=models.CASCADE)


class PageLearningObject(models.Model):
    class Meta:
        db_table = 'page_learning_object'

    type = models.CharField(max_length=10, null=True)
    path = models.TextField()
    title = models.CharField(max_length=256, null=True)
    file_name = models.CharField(max_length=256, null=True, blank=True)
    preview_path = models.URLField(null=True)
    disabled = models.BooleanField(default=False)
    dir_len = models.IntegerField(default=0)
    is_webpage = models.BooleanField(default=False)
    learning_object = models.ForeignKey(LearningObject, related_name="page_learning_object", on_delete=models.CASCADE)


class TagPageLearningObject(models.Model):
    class Meta:
        db_table = 'tag_page_learning_object'

    tag = models.CharField(max_length=20)
    text = models.TextField(null=True, blank=True)
    html_text = models.TextField(null=True, blank=True)
    id_class_ref = models.CharField(max_length=20)
    adapting = models.BooleanField(default=False, null=True)
    adaptation = models.BooleanField(default=True)
    page_learning_object = models.ForeignKey(PageLearningObject, related_name="tag_page_learning_object",
                                             on_delete=models.CASCADE)


class TagAdapted(models.Model):
    class Meta:
        db_table = 'tag_adapted'

    type = models.CharField(max_length=20)
    text = models.TextField(null=True, blank=True)
    html_text = models.TextField(null=True, blank=True)
    id_ref = models.CharField(max_length=20, null=True)
    path_src = models.TextField(null=True, blank=True)
    path_system = models.TextField(null=True, blank=True)
    path_preview = models.URLField(max_length=255, null=True)
    button_text_id = models.CharField(max_length=20, null=True)
    button_audio_id = models.CharField(max_length=20, null=True)
    text_table = models.TextField(null=True, blank=True)
    img_fullscreen = models.BooleanField(default=False)

    image_map = models.TextField(null=True)
    image_map_reference_data = models.TextField(null=True)
    image_map_reference_coordinates = models.TextField(null=True)

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
    source = models.CharField(max_length=50, null=True, blank=True)
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
    tag_page_learning_object = models.ForeignKey(TagPageLearningObject, related_name="attributes",
                                                 on_delete=models.CASCADE)


class MetadataInfo(models.Model):
    class Meta:
        db_table = 'metadata_info'

    browser = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    text_number = models.IntegerField(default=0)
    video_number = models.IntegerField(default=0)
    audio_number = models.IntegerField(default=0)
    img_number = models.IntegerField(default=0)
    id_learning = models.IntegerField(default=0)


class RequestApi(models.Model):
    class Meta:
        db_table = 'request_api'

    email = models.EmailField(max_length=50)
    institution = models.CharField(max_length=100, null=True, blank=True)
    purpose_use = models.TextField()
    api_key = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
