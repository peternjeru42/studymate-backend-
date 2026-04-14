from django.contrib import admin

from apps.notifications.models import Notification, NotificationTemplate, ReminderQueue

admin.site.register(Notification)
admin.site.register(NotificationTemplate)
admin.site.register(ReminderQueue)
