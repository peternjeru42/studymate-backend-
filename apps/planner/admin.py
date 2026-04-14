from django.contrib import admin

from apps.planner.models import AvailabilityBlock, PlanAdjustmentLog, PlanSource, StudyPlan, StudySession

admin.site.register(AvailabilityBlock)
admin.site.register(StudyPlan)
admin.site.register(StudySession)
admin.site.register(PlanSource)
admin.site.register(PlanAdjustmentLog)
