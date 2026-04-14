from rest_framework import serializers

from apps.notifications.models import Notification, NotificationTemplate, ReminderQueue


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = "__all__"


class ReminderQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderQueue
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")
