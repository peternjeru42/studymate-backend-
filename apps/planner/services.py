from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import StudyPreference
from apps.academics.models import Course
from apps.ai_engine.services import PromptBuilderService, ScenarioRecommendationService, StudyPlanGeneratorService
from apps.assessments.models import Assessment
from apps.calendar_app.models import CalendarEvent
from apps.notifications.models import Notification
from apps.planner.models import PlanAdjustmentLog, PlanSource, StudyPlan, StudySession
from apps.recommendations.models import Recommendation
from apps.tasks.models import Task


class PlannerOrchestratorService:
    @staticmethod
    def _resolve_source(user, validated_data):
        task = None
        assessment = None
        course = None
        topic = validated_data.get("topic")
        deadline = validated_data.get("deadline")
        available_hours = validated_data.get("available_hours")

        if "task_id" in validated_data:
            task = Task.objects.filter(user=user, id=validated_data["task_id"]).select_related("course").first()
            if task:
                topic = topic or task.title
                deadline = deadline or task.due_date
                available_hours = available_hours or task.estimated_hours
                course = task.course

        if "assessment_id" in validated_data:
            assessment = (
                Assessment.objects.filter(user=user, id=validated_data["assessment_id"]).select_related("course").first()
            )
            if assessment:
                topic = topic or assessment.title
                deadline = deadline or assessment.date
                available_hours = available_hours or assessment.estimated_study_hours
                course = course or assessment.course

        if "course_id" in validated_data:
            course = Course.objects.filter(user=user, id=validated_data["course_id"]).first() or course

        topic = topic or "Study Plan"
        deadline = deadline or timezone.now() + timedelta(days=7)
        available_hours = Decimal(available_hours or 5)
        return task, assessment, course, topic, deadline, available_hours

    @staticmethod
    def _default_start_for_preference(user, date_value):
        preference = getattr(user, "study_preference", None)
        start_hour = 18
        if preference:
            mapping = {
                StudyPreference.PreferredStudyTime.MORNING: 8,
                StudyPreference.PreferredStudyTime.AFTERNOON: 14,
                StudyPreference.PreferredStudyTime.EVENING: 18,
                StudyPreference.PreferredStudyTime.NIGHT: 22,
            }
            start_hour = mapping.get(preference.preferred_study_time, 18)
        return timezone.make_aware(datetime.combine(date_value, time(hour=start_hour)))

    @classmethod
    def _build_draft(cls, *, topic, deadline, available_hours, difficulty, mode, notes):
        days_until = max(1, (deadline.date() - timezone.now().date()).days)
        session_count = max(1, min(days_until, int(available_hours) if available_hours > 1 else 1))
        hours_per_session = max(1, float(available_hours) / session_count)
        study_sessions = []
        risk_alerts = []
        if days_until <= 2:
            risk_alerts.append("Very short runway before the deadline. Keep sessions focused and reduce context switching.")
        if available_hours < 3:
            risk_alerts.append("Limited available hours. Prioritize the highest-yield material first.")
        for index in range(session_count):
            learning_method = (
                StudySession.LearningMethod.PRACTICE_PROBLEMS
                if mode in {StudyPlan.Mode.EXAM_PREP, StudyPlan.Mode.CATCH_UP}
                else StudySession.LearningMethod.ACTIVE_RECALL
            )
            study_sessions.append(
                {
                    "day_number": index + 1,
                    "topic": f"{topic} - Session {index + 1}",
                    "focus_areas": [topic, f"Priority block {index + 1}"],
                    "estimated_time": round(hours_per_session, 2),
                    "learning_method": learning_method,
                    "notes": notes or "",
                }
            )
        return {
            "topic": topic,
            "deadline": deadline.isoformat(),
            "available_hours": float(available_hours),
            "difficulty": difficulty,
            "mode": mode,
            "notes": notes,
            "study_sessions": study_sessions,
            "risk_alerts": risk_alerts,
        }

    @classmethod
    @transaction.atomic
    def generate_plan(cls, *, user, validated_data):
        task, assessment, course, topic, deadline, available_hours = cls._resolve_source(user, validated_data)
        difficulty = validated_data.get("difficulty", StudyPlan.Difficulty.MEDIUM)
        mode = validated_data.get("mode", StudyPlan.Mode.DEEP_STUDY)
        notes = validated_data.get("notes", "")
        draft = cls._build_draft(
            topic=topic,
            deadline=deadline,
            available_hours=available_hours,
            difficulty=difficulty,
            mode=mode,
            notes=notes,
        )
        resolved_context = {
            "task_id": str(task.id) if task else None,
            "assessment_id": str(assessment.id) if assessment else None,
            "course_id": str(course.id) if course else None,
        }
        context = ScenarioRecommendationService.build_plan_generation_context(
            user=user, input_payload=validated_data, resolved_context=resolved_context
        )
        prompt = PromptBuilderService.build_study_plan_prompt(draft)
        ai_payload = StudyPlanGeneratorService.generate(
            user=user, draft=draft, request_payload=prompt, context=context
        )
        plan = StudyPlan.objects.create(
            user=user,
            topic=topic,
            deadline=deadline,
            duration=available_hours,
            available_hours=available_hours,
            difficulty=difficulty,
            mode=mode,
            notes=notes,
            source_task=task,
            source_assessment=assessment,
            course=course,
            revision_milestones=ai_payload.get("revision_milestones", []),
            retention_tips=ai_payload.get("retention_tips", []),
            risk_alerts=ai_payload.get("risk_alerts", []),
        )
        PlanSource.objects.create(
            user=user,
            plan=plan,
            source_type="assessment" if assessment else "task" if task else "manual",
            task=task,
            assessment=assessment,
            course=course,
            metadata=resolved_context,
        )
        for session_payload in ai_payload.get("study_sessions", []):
            scheduled_date = timezone.now().date() + timedelta(days=session_payload["day_number"] - 1)
            scheduled_start = cls._default_start_for_preference(user, scheduled_date)
            estimated_time = Decimal(str(session_payload["estimated_time"]))
            scheduled_end = scheduled_start + timedelta(hours=float(estimated_time))
            StudySession.objects.create(
                user=user,
                plan=plan,
                day_number=session_payload["day_number"],
                topic=session_payload["topic"],
                focus_areas=session_payload.get("focus_areas", []),
                estimated_time=estimated_time,
                learning_method=session_payload.get("learning_method", StudySession.LearningMethod.ACTIVE_RECALL),
                notes=session_payload.get("notes", ""),
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                task=task,
                assessment=assessment,
                course=course,
            )
        if plan.risk_alerts:
            Recommendation.objects.create(
                user=user,
                title=f"Plan risk detected for {plan.topic}",
                description=plan.risk_alerts[0],
                urgency="high",
                category="deadline-risk",
                suggested_action="Review the generated plan and reduce competing commitments.",
                action_type="plan",
                related_item_type="study_plan",
                related_item_id=str(plan.id),
            )
            Notification.objects.create(
                user=user,
                type="alert",
                title="Study plan generated with risks",
                message=plan.risk_alerts[0],
                related_item_type="study_plan",
                related_item_id=str(plan.id),
            )
        return plan

    @staticmethod
    def apply_to_calendar(*, user, plan):
        created_events = []
        for session in plan.study_sessions.all():
            event = CalendarEvent.objects.create(
                user=user,
                title=session.topic,
                description=session.notes,
                start_time=session.scheduled_start or timezone.now(),
                end_time=session.scheduled_end or (timezone.now() + timedelta(hours=float(session.estimated_time))),
                source_type="study_session",
                event_type="study",
                linked_task=session.task,
                linked_assessment=session.assessment,
                linked_plan=plan,
                linked_session=session,
            )
            created_events.append(event)
        plan.applied_to_calendar = True
        plan.save(update_fields=["applied_to_calendar", "updated_at"])
        return created_events

    @staticmethod
    def convert_to_tasks(*, user, plan):
        tasks = []
        course = plan.course or (plan.source_task.course if plan.source_task else None)
        if not course and plan.source_assessment:
            course = plan.source_assessment.course
        for session in plan.study_sessions.all():
            task = Task.objects.create(
                user=user,
                course=course,
                title=session.topic,
                description=session.notes,
                type=Task.TaskType.READING,
                due_date=session.scheduled_end or plan.deadline,
                priority=Task.Priority.MEDIUM,
                status=Task.Status.NOT_STARTED,
                estimated_hours=session.estimated_time,
                notes=f"Generated from plan {plan.topic}",
            )
            tasks.append(task)
        PlanAdjustmentLog.objects.create(
            user=user,
            plan=plan,
            action="convert_to_tasks",
            reason="Converted study sessions to standalone tasks.",
            metadata={"task_ids": [str(task.id) for task in tasks]},
        )
        return tasks

    @classmethod
    def regenerate_plan(cls, *, user, plan):
        PlanAdjustmentLog.objects.create(
            user=user,
            plan=plan,
            action="regenerate",
            reason="Plan regenerated by user request.",
        )
        validated_data = {
            "topic": plan.topic,
            "deadline": plan.deadline,
            "available_hours": plan.available_hours,
            "difficulty": plan.difficulty,
            "mode": plan.mode,
            "notes": plan.notes,
        }
        if plan.source_task_id:
            validated_data["task_id"] = plan.source_task_id
        if plan.source_assessment_id:
            validated_data["assessment_id"] = plan.source_assessment_id
        if plan.course_id:
            validated_data["course_id"] = plan.course_id
        return cls.generate_plan(user=user, validated_data=validated_data)
