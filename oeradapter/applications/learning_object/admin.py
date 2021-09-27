from django.contrib import admin
from .models import LearningObject, LearningObjectAdaptation

# Register your models here.
admin.site.register(LearningObject)
admin.site.register(LearningObjectAdaptation)
