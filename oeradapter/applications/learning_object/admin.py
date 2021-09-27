from django.contrib import admin
from .models import LearningObject, AdaptationLearningObject, PageLearningObject, TagPageLearningObject

# Register your models here.
admin.site.register(LearningObject)
admin.site.register(AdaptationLearningObject)
admin.site.register(PageLearningObject)
admin.site.register(TagPageLearningObject)
