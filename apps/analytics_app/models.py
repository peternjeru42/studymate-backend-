from django.db import models

from apps.academics.models import Course
from apps.common.models import OwnedByUserModel, TimeStampedModel, UUIDPrimaryKeyModel


class StudyMetric(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    metric_name = models.CharField(max_length=120)
    metric_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    recorded_for = models.DateField()

    class Meta:
        ordering = ("-recorded_for",)

    def __str__(self):
        return self.metric_name


class DailyProgress(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    date = models.DateField()
    study_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    tasks_completed = models.PositiveIntegerField(default=0)
    sessions_completed = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "date")

    def __str__(self):
        return str(self.date)


class CourseProgress(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="progress_records")
    completion_percent = models.PositiveIntegerField(default=0)
    on_time_rate = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.course.code} progress"


class StreakRecord(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} streak"
