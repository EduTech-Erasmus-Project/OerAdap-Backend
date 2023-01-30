from django.contrib import admin
from .models import LearningObject, AdaptationLearningObject, PageLearningObject, Transcript, DataAttribute, MetadataInfo, TagPageLearningObject, TagAdapted

# Register your models here.
admin.site.register(LearningObject)
admin.site.register(AdaptationLearningObject)
admin.site.register(PageLearningObject)
admin.site.register(TagPageLearningObject)
admin.site.register(TagAdapted)
admin.site.register(Transcript)
admin.site.register(DataAttribute)
admin.site.register(MetadataInfo)
