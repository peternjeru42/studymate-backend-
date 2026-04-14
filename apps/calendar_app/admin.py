from django.contrib import admin

from apps.calendar_app.models import CalendarEvent, EventReminder, FreeTimeWindow

admin.site.register(CalendarEvent)
admin.site.register(EventReminder)
admin.site.register(FreeTimeWindow)
