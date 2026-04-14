from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel, UUIDPrimaryKeyModel


class User(AbstractUser, UUIDPrimaryKeyModel, TimeStampedModel):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def __str__(self):
        return self.email


class StudentProfile(UUIDPrimaryKeyModel, TimeStampedModel):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="student_profile")
    institution = models.CharField(max_length=255, blank=True)
    academic_level = models.CharField(max_length=100, blank=True)
    current_semester = models.CharField(max_length=100, blank=True)
    target_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    weekly_study_target_hours = models.PositiveIntegerField(default=10)
    onboarding_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} profile"


class StudyPreference(UUIDPrimaryKeyModel, TimeStampedModel):
    class PreferredStudyTime(models.TextChoices):
        MORNING = "morning", "Morning"
        AFTERNOON = "afternoon", "Afternoon"
        EVENING = "evening", "Evening"
        NIGHT = "night", "Night"

    class StudyStyle(models.TextChoices):
        VISUAL = "visual", "Visual"
        AUDITORY = "auditory", "Auditory"
        KINESTHETIC = "kinesthetic", "Kinesthetic"
        READING = "reading", "Reading/Writing"

    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="study_preference")
    preferred_study_time = models.CharField(max_length=20, choices=PreferredStudyTime.choices, default=PreferredStudyTime.EVENING)
    session_duration = models.PositiveIntegerField(default=90)
    break_duration = models.PositiveIntegerField(default=15)
    study_style = models.CharField(max_length=20, choices=StudyStyle.choices, default=StudyStyle.VISUAL)
    max_sessions_per_day = models.PositiveIntegerField(default=3)

    def __str__(self):
        return f"{self.user.email} study preference"


class NotificationPreference(UUIDPrimaryKeyModel, TimeStampedModel):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="notification_preference")
    deadline_reminders = models.BooleanField(default=True)
    study_suggestions = models.BooleanField(default=True)
    assessment_alerts = models.BooleanField(default=True)
    daily_summary = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} notification preference"
