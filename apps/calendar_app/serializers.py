from rest_framework import serializers

from apps.calendar_app.models import CalendarEvent, EventReminder, FreeTimeWindow


class EventReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventReminder
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CalendarEventSerializer(serializers.ModelSerializer):
    reminders = EventReminderSerializer(many=True, read_only=True)

    class Meta:
        model = CalendarEvent
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class FreeTimeWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeTimeWindow
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")
