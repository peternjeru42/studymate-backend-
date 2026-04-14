from django.contrib import admin

from apps.tasks.models import Task, TaskTag

admin.site.register(Task)
admin.site.register(TaskTag)
