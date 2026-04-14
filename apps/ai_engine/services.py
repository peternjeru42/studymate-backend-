import json

from django.conf import settings

from apps.ai_engine.models import AIRequestLog, AIResponseLog, PlanGenerationContext


class PromptBuilderService:
    @staticmethod
    def build_study_plan_prompt(draft):
        return {
            "instructions": (
                "You are generating a personalized study plan for a student. "
                "Return only JSON that matches the required schema. "
                "Use the provided topic, deadline, available hours, difficulty, mode, and any notes to produce a realistic schedule. "
                "Distribute the work across the available sessions, keep focus areas specific, and include practical retention tips and risk alerts when warranted."
            ),
            "context": draft,
        }


class ResponseValidatorService:
    required_keys = ("study_sessions", "revision_milestones", "retention_tips", "risk_alerts")

    @classmethod
    def validate(cls, payload):
        errors = []
        if not isinstance(payload, dict):
            return ["Response payload must be a JSON object."]
        for key in cls.required_keys:
            if key not in payload:
                errors.append(f"Missing key: {key}")
        for key in cls.required_keys:
            if key in payload and not isinstance(payload[key], list):
                errors.append(f"{key} must be a list.")
        return errors


class AIServiceError(Exception):
    def __init__(self, message, *, details=None):
        super().__init__(message)
        self.details = details or [message]


class OpenAIResponseService:
    @staticmethod
    def generate_json(*, instructions, input_payload, schema_name, schema, user_identifier=None):
        if not settings.OPENAI_API_KEY:
            raise AIServiceError("OPENAI_API_KEY is not configured on the Railway backend.")

        if not settings.OPENAI_MODEL:
            raise AIServiceError("OPENAI_MODEL is not configured on the Railway backend.")

        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise AIServiceError("The OpenAI SDK is not installed on the Railway backend.") from exc

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        try:
            response = client.responses.create(
                model=settings.OPENAI_MODEL,
                instructions=instructions,
                input=json.dumps(input_payload, default=str),
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "schema": schema,
                        "strict": True,
                    },
                    "verbosity": "medium",
                },
                store=False,
                user=user_identifier,
            )
        except Exception as exc:  # pragma: no cover
            raise AIServiceError("OpenAI request failed for this feature.", details=[str(exc)]) from exc

        output_text = getattr(response, "output_text", "")
        if not output_text:
            raise AIServiceError("OpenAI returned an empty response.")

        try:
            return json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise AIServiceError("OpenAI returned invalid JSON.", details=[str(exc)]) from exc


class StudyPlanGeneratorService:
    @staticmethod
    def response_schema():
        return {
            "type": "object",
            "properties": {
                "study_sessions": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "day_number": {"type": "integer", "minimum": 1},
                            "topic": {"type": "string", "minLength": 1},
                            "focus_areas": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "estimated_time": {"type": "number", "minimum": 0.25},
                            "learning_method": {
                                "type": "string",
                                "enum": [
                                    "active-recall",
                                    "spaced-repetition",
                                    "interleaving",
                                    "practice-problems",
                                ],
                            },
                            "notes": {"type": "string"},
                        },
                        "required": [
                            "day_number",
                            "topic",
                            "focus_areas",
                            "estimated_time",
                            "learning_method",
                            "notes",
                        ],
                        "additionalProperties": False,
                    },
                },
                "revision_milestones": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "day": {"type": "integer", "minimum": 1},
                            "milestone": {"type": "string", "minLength": 1},
                            "review_topics": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["day", "milestone", "review_topics"],
                        "additionalProperties": False,
                    },
                },
                "retention_tips": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "risk_alerts": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["study_sessions", "revision_milestones", "retention_tips", "risk_alerts"],
            "additionalProperties": False,
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
        try:
            payload = OpenAIResponseService.generate_json(
                instructions=request_payload["instructions"],
                input_payload=request_payload["context"],
                schema_name="study_plan",
                schema=cls.response_schema(),
                user_identifier=str(user.id),
            )
            validation_errors = ResponseValidatorService.validate(payload)
            if validation_errors:
                raise AIServiceError("OpenAI returned an invalid study plan payload.", details=validation_errors)
        except AIServiceError as exc:
            request_log.status = "failed"
            request_log.save(update_fields=["status", "updated_at"])
            AIResponseLog.objects.create(
                request=request_log,
                response_payload={},
                validation_errors=exc.details,
                status="error",
            )
            raise

        request_log.status = "completed"
        request_log.save(update_fields=["status", "updated_at"])
        AIResponseLog.objects.create(
            request=request_log,
            response_payload=payload,
            validation_errors=[],
            status="success",
        )
        return payload


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
