from django.db import models

from apps.common.models import OwnedByUserModel, TimeStampedModel, UUIDPrimaryKeyModel


class PromptTemplate(UUIDPrimaryKeyModel, TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    system_prompt = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PlanGenerationContext(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    input_payload = models.JSONField(default=dict, blank=True)
    resolved_context = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Plan context {self.id}"


class AIRequestLog(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    feature = models.CharField(max_length=100)
    model = models.CharField(max_length=120, blank=True)
    request_payload = models.JSONField(default=dict, blank=True)
    context = models.ForeignKey(
        PlanGenerationContext,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="request_logs",
    )
    status = models.CharField(max_length=30, default="pending")

    def __str__(self):
        return f"{self.feature} request"


class AIResponseLog(UUIDPrimaryKeyModel, TimeStampedModel):
    request = models.OneToOneField(AIRequestLog, on_delete=models.CASCADE, related_name="response_log")
    response_payload = models.JSONField(default=dict, blank=True)
    validation_errors = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=30, default="success")

    def __str__(self):
        return f"{self.request.feature} response"
