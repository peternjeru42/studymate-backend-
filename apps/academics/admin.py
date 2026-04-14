from django.contrib import admin

from apps.academics.models import Course, Enrollment, Semester, Subtopic, Topic

admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Topic)
admin.site.register(Subtopic)
