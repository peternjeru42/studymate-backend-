from django.contrib import admin

from apps.analytics_app.models import CourseProgress, DailyProgress, StreakRecord, StudyMetric

admin.site.register(StudyMetric)
admin.site.register(DailyProgress)
admin.site.register(CourseProgress)
admin.site.register(StreakRecord)
