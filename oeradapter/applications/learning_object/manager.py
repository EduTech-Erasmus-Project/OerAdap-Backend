from django.db import models

class LearningObjectManager(models.Manager):

    def post_upload_file(self):
        pass
