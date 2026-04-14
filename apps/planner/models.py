from django.db import models

from apps.academics.models import Course, Topic
from apps.assessments.models import Assessment
from apps.common.models import OwnedByUserModel, TimeStampedModel, UUIDPrimaryKeyModel
from apps.tasks.models import Task


class AvailabilityBlock(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    day_of_week = models.PositiveSmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ("day_of_week", "start_time")

    def __str__(self):
        return f"{self.day_of_week}: {self.start_time}-{self.end_time}"


class StudyPlan(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    class Mode(models.TextChoices):
        REVISION = "revision", "Revision"
        DEEP_STUDY = "deep-study", "Deep Study"
        EXAM_PREP = "exam-prep", "Exam Prep"
        QUICK_REVIEW = "quick-review", "Quick Review"
        CATCH_UP = "catch-up", "Catch Up"

    topic = models.CharField(max_length=255)
    deadline = models.DateTimeField()
    duration = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    available_hours = models.DecimalField(max_digits=6, decimal_places=2, default=1)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.DEEP_STUDY)
    notes = models.TextField(blank=True)
    source_task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL, related_name="study_plans")
    source_assessment = models.ForeignKey(
        Assessment, null=True, blank=True, on_delete=models.SET_NULL, related_name="study_plans"
    )
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL, related_name="study_plans")
    revision_milestones = models.JSONField(default=list, blank=True)
    retention_tips = models.JSONField(default=list, blank=True)
    risk_alerts = models.JSONField(default=list, blank=True)
    is_saved = models.BooleanField(default=False)
    applied_to_calendar = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.topic


class StudySession(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    class LearningMethod(models.TextChoices):
        ACTIVE_RECALL = "active-recall", "Active Recall"
        SPACED_REPETITION = "spaced-repetition", "Spaced Repetition"
        INTERLEAVING = "interleaving", "Interleaving"
        PRACTICE_PROBLEMS = "practice-problems", "Practice Problems"

    plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name="study_sessions")
    day_number = models.PositiveIntegerField(default=1)
    topic = models.CharField(max_length=255)
    focus_areas = models.JSONField(default=list, blank=True)
    estimated_time = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    learning_method = models.CharField(
        max_length=32, choices=LearningMethod.choices, default=LearningMethod.ACTIVE_RECALL
    )
    notes = models.TextField(blank=True)
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL, related_name="study_sessions")
    assessment = models.ForeignKey(
        Assessment, null=True, blank=True, on_delete=models.SET_NULL, related_name="study_sessions"
    )
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL, related_name="study_sessions")
    topic_link = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL, related_name="study_sessions")

    class Meta:
        ordering = ("day_number", "created_at")

    def __str__(self):
        return f"{self.plan.topic} day {self.day_number}"


class PlanSource(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    plan = models.OneToOneField(StudyPlan, on_delete=models.CASCADE, related_name="plan_source")
    source_type = models.CharField(max_length=30, default="manual")
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL)
    assessment = models.ForeignKey(Assessment, null=True, blank=True, on_delete=models.SET_NULL)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.source_type} source"


class PlanAdjustmentLog(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name="adjustment_logs")
    action = models.CharField(max_length=50)
    reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.action} for {self.plan.topic}"
