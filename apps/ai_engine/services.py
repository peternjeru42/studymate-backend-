import json
from math import ceil

from django.conf import settings

from apps.ai_engine.models import AIRequestLog, AIResponseLog, PlanGenerationContext


class PromptBuilderService:
    @staticmethod
    def build_study_plan_prompt(draft):
        return {
            "instructions": (
                "Return strict JSON with keys study_sessions, revision_milestones, retention_tips, risk_alerts. "
                "Keep each value concise and aligned to the provided schedule."
            ),
            "context": draft,
        }


class ResponseValidatorService:
    required_keys = ("study_sessions", "revision_milestones", "retention_tips", "risk_alerts")

    @classmethod
    def validate(cls, payload):
        errors = []
        for key in cls.required_keys:
            if key not in payload:
                errors.append(f"Missing key: {key}")
        return errors


class StudyPlanGeneratorService:
    @staticmethod
    def fallback_payload(draft):
        session_count = max(1, len(draft["study_sessions"]))
        return {
            "study_sessions": draft["study_sessions"],
            "revision_milestones": [
                {
                    "day": min(session_count, max(1, ceil(session_count / 2))),
                    "milestone": f"Solidify the core concepts for {draft['topic']}",
                    "review_topics": [draft["topic"]],
                }
            ],
            "retention_tips": [
                "Review your notes within 24 hours of each session.",
                "Use active recall before reading solutions.",
                "Summarize each session in one paragraph.",
            ],
            "risk_alerts": draft.get("risk_alerts", []),
        }

    @classmethod
    def generate(cls, *, user, draft, request_payload, context):
        request_log = AIRequestLog.objects.create(
            user=user,
            feature="study-plan",
            model=settings.OPENAI_MODEL,
            request_payload=request_payload,
            context=context,
            status="pending",
        )
        payload = None
        errors = []
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.responses.create(
                    model=settings.OPENAI_MODEL,
                    input=[
                        {"role": "system", "content": request_payload["instructions"]},
                        {"role": "user", "content": json.dumps(request_payload["context"], default=str)},
                    ],
                )
                payload = json.loads(response.output_text)
            except Exception as exc:  # pragma: no cover
                errors = [str(exc)]

        if payload is None:
            payload = cls.fallback_payload(draft)

        validation_errors = ResponseValidatorService.validate(payload)
        request_log.status = "completed" if not validation_errors else "fallback"
        request_log.save(update_fields=["status", "updated_at"])
        AIResponseLog.objects.create(
            request=request_log,
            response_payload=payload,
            validation_errors=validation_errors + errors,
            status="success" if not validation_errors else "fallback",
        )
        return payload if not validation_errors else cls.fallback_payload(draft)


class ScenarioRecommendationService:
    @staticmethod
    def build_plan_generation_context(*, user, input_payload, resolved_context):
        normalized_input = json.loads(json.dumps(input_payload, default=str))
        normalized_context = json.loads(json.dumps(resolved_context, default=str))
        return PlanGenerationContext.objects.create(
            user=user,
            input_payload=normalized_input,
            resolved_context=normalized_context,
        )
