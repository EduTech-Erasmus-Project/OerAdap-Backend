from django.db import models
from .manager import LearningObjectManager
import shortuuid
import os
import random


def directory_path(instance, filename):
    uuid = str(shortuuid.ShortUUID().random(length=8))
    path = "uploads/"+filename.split('.')[0]
    return os.path.join(path, filename)


# Create your models here.
class LearningObject(models.Model):
    path_origin = models.CharField(max_length=100, blank=True, null=True)
    path_adapted = models.CharField(max_length=100, blank=True, null=True)
    user_ref = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(upload_to=directory_path)

    objects = LearningObjectManager()

    def __str__(self):
        return str(self.file)

    def save_path(self):
        #self.path_origin = self.file.path
        print("path file " + str(self.file.path))

    def save(self, *args, **kwargs):
        self.save_path()
        super(LearningObject, self).save(*args, **kwargs)



