from django.db import models

from apps.common.models import OwnedByUserModel, TimeStampedModel, UUIDPrimaryKeyModel


class Recommendation(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    class Urgency(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Category(models.TextChoices):
        DEADLINE_RISK = "deadline-risk", "Deadline Risk"
        STUDY_HABITS = "study-habits", "Study Habits"
        PERFORMANCE = "performance", "Performance"
        WORKLOAD = "workload", "Workload"
        HEALTH = "health", "Health"

    title = models.CharField(max_length=255)
    description = models.TextField()
    urgency = models.CharField(max_length=20, choices=Urgency.choices, default=Urgency.MEDIUM)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.WORKLOAD)
    suggested_action = models.TextField()
    action_type = models.CharField(max_length=30, default="plan")
    related_item_type = models.CharField(max_length=50, blank=True)
    related_item_id = models.CharField(max_length=64, blank=True)
    is_dismissed = models.BooleanField(default=False)
    is_applied = models.BooleanField(default=False)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class RecommendationRule(UUIDPrimaryKeyModel, TimeStampedModel):
    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class RecommendationActionLog(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, related_name="action_logs")
    action = models.CharField(max_length=50)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.action} - {self.recommendation.title}"
