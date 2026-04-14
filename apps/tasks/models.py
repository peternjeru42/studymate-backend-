from django.db import models
from django.utils import timezone

from apps.academics.models import Course
from apps.common.models import OwnedByUserModel, TimeStampedModel, UUIDPrimaryKeyModel


class TaskTag(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=32, default="bg-gray-500")

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return self.name


class Task(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    class TaskType(models.TextChoices):
        ASSIGNMENT = "assignment", "Assignment"
        READING = "reading", "Reading"
        PROJECT = "project", "Project"
        QUIZ = "quiz", "Quiz"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        NOT_STARTED = "not-started", "Not Started"
        IN_PROGRESS = "in-progress", "In Progress"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"

    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.OTHER)
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.ManyToManyField(TaskTag, blank=True, related_name="tasks")

    class Meta:
        ordering = ("due_date", "-priority")

    def save(self, *args, **kwargs):
        if self.status != self.Status.COMPLETED and self.due_date < timezone.now():
            self.status = self.Status.OVERDUE
        super().save(*args, **kwargs)

    @property
    def effective_status(self):
        if self.status != self.Status.COMPLETED and self.due_date < timezone.now():
            return self.Status.OVERDUE
        return self.status

    def __str__(self):
        return self.title
