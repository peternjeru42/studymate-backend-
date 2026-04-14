from django.db import models

from apps.academics.models import Course, Topic
from apps.common.models import OwnedByUserModel, TimeStampedModel, UUIDPrimaryKeyModel


class Assessment(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    class AssessmentType(models.TextChoices):
        EXAM = "exam", "Exam"
        TEST = "test", "Test"
        QUIZ = "quiz", "Quiz"
        PRESENTATION = "presentation", "Presentation"
        PROJECT = "project", "Project"

    class PrepStatus(models.TextChoices):
        NOT_STARTED = "not-started", "Not Started"
        STARTED = "started", "Started"
        PREPARED = "prepared", "Prepared"
        READY = "ready", "Ready"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assessments")
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=AssessmentType.choices, default=AssessmentType.EXAM)
    date = models.DateTimeField()
    weight = models.PositiveIntegerField(default=0)
    prep_status = models.CharField(max_length=20, choices=PrepStatus.choices, default=PrepStatus.NOT_STARTED)
    estimated_study_hours = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    passing_score = models.PositiveIntegerField(null=True, blank=True)
    current_score = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ("date",)

    def __str__(self):
        return self.title


class AssessmentTopic(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="assessment_topics")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="assessment_topics")

    class Meta:
        unique_together = ("assessment", "topic")

    def __str__(self):
        return f"{self.assessment.title} -> {self.topic.title}"


class AssessmentPreparationStatus(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name="preparation_status")
    confidence_level = models.PositiveIntegerField(default=1)
    readiness_notes = models.TextField(blank=True)
    progress_percent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.assessment.title} prep"
