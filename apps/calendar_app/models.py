from django.db import models

from apps.assessments.models import Assessment
from apps.common.models import OwnedByUserModel, TimeStampedModel, UUIDPrimaryKeyModel
from apps.tasks.models import Task


class CalendarEvent(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    source_type = models.CharField(max_length=30, default="custom")
    event_type = models.CharField(max_length=30, default="study")
    all_day = models.BooleanField(default=False)
    linked_task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL, related_name="calendar_events")
    linked_assessment = models.ForeignKey(
        Assessment, null=True, blank=True, on_delete=models.SET_NULL, related_name="calendar_events"
    )
    linked_plan = models.ForeignKey(
        "planner.StudyPlan", null=True, blank=True, on_delete=models.SET_NULL, related_name="calendar_events"
    )
    linked_session = models.ForeignKey(
        "planner.StudySession", null=True, blank=True, on_delete=models.SET_NULL, related_name="calendar_events"
    )

    class Meta:
        ordering = ("start_time",)

    def __str__(self):
        return self.title


class EventReminder(UUIDPrimaryKeyModel, TimeStampedModel):
    event = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name="reminders")
    minutes_before = models.PositiveIntegerField(default=30)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.minutes_before} minutes before"


class FreeTimeWindow(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    source = models.CharField(max_length=50, default="manual")

    class Meta:
        ordering = ("start_time",)

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"
