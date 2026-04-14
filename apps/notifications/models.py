from django.db import models

from apps.common.models import OwnedByUserModel, TimeStampedModel, UUIDPrimaryKeyModel


class Notification(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    type = models.CharField(max_length=30, default="reminder")
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_item_type = models.CharField(max_length=50, blank=True)
    related_item_id = models.CharField(max_length=64, blank=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ("read", "-created_at")

    def __str__(self):
        return self.title


class NotificationTemplate(UUIDPrimaryKeyModel, TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ReminderQueue(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    reminder_type = models.CharField(max_length=50)
    scheduled_for = models.DateTimeField()
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=30, default="pending")

    class Meta:
        ordering = ("scheduled_for",)

    def __str__(self):
        return f"{self.reminder_type} @ {self.scheduled_for}"
