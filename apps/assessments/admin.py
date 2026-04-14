from django.contrib import admin

from apps.assessments.models import Assessment, AssessmentPreparationStatus, AssessmentTopic

admin.site.register(Assessment)
admin.site.register(AssessmentTopic)
admin.site.register(AssessmentPreparationStatus)
