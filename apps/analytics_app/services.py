from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from apps.assessments.models import Assessment
from apps.notifications.models import Notification
from apps.planner.models import StudySession
from apps.recommendations.models import Recommendation
from apps.tasks.models import Task


class AnalyticsService:
    @staticmethod
    def dashboard(user):
        now = timezone.now()
        today = now.date()
        study_sessions = StudySession.objects.filter(user=user, scheduled_start__date=today)
        upcoming_tasks = Task.objects.filter(user=user, due_date__gte=now).order_by("due_date")[:5]
        overdue_tasks = Task.objects.filter(user=user, due_date__lt=now).exclude(status=Task.Status.COMPLETED)
        next_assessment = Assessment.objects.filter(user=user, date__gte=now).order_by("date").first()
        weekly_session_hours = defaultdict(float)
        start_of_week = today - timedelta(days=today.weekday())
        sessions = StudySession.objects.filter(user=user, scheduled_start__date__gte=start_of_week)
        for session in sessions:
            weekly_session_hours[session.scheduled_start.weekday()] += float(session.estimated_time)
        weekly_hours = [round(weekly_session_hours.get(index, 0), 2) for index in range(7)]
        urgent_recommendations = Recommendation.objects.filter(
            user=user, is_dismissed=False, urgency__in=["high", "critical"]
        )[:5]
        unread_notifications = Notification.objects.filter(user=user, read=False).count()
        completed_tasks = Task.objects.filter(user=user, status=Task.Status.COMPLETED).count()
        total_tasks = Task.objects.filter(user=user).count()
        return {
            "todays_study_sessions": [
                {
                    "id": str(item.id),
                    "topic": item.topic,
                    "start_time": item.scheduled_start,
                    "end_time": item.scheduled_end,
                }
                for item in study_sessions
            ],
            "upcoming_deadlines": [
                {
                    "id": str(item.id),
                    "title": item.title,
                    "due_date": item.due_date,
                }
                for item in upcoming_tasks
            ],
            "overdue_tasks": [
                {
                    "id": str(item.id),
                    "title": item.title,
                    "due_date": item.due_date,
                }
                for item in overdue_tasks
            ],
            "next_assessment": {
                "id": str(next_assessment.id),
                "title": next_assessment.title,
                "date": next_assessment.date,
            }
            if next_assessment
            else None,
            "weekly_progress": {
                "completed_tasks": completed_tasks,
                "total_tasks": total_tasks,
                "weekly_hours": weekly_hours,
            },
            "urgent_recommendations": [str(item.id) for item in urgent_recommendations],
            "unread_notifications_count": unread_notifications,
        }

    @staticmethod
    def progress(user):
        completed_sessions = StudySession.objects.filter(user=user, completed=True)
        total_hours = sum(float(item.estimated_time) for item in completed_sessions)
        completed_tasks = Task.objects.filter(user=user, status=Task.Status.COMPLETED).count()
        total_tasks = Task.objects.filter(user=user).count()
        overdue_tasks = Task.objects.filter(user=user, due_date__lt=timezone.now()).exclude(status=Task.Status.COMPLETED).count()
        return {
            "total_study_hours": round(total_hours, 2),
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "overdue_tasks": overdue_tasks,
        }

    @staticmethod
    def course_progress(user):
        payload = []
        course_ids = Task.objects.filter(user=user).values_list("course_id", flat=True).distinct()
        for course_id in course_ids:
            if not course_id:
                continue
            tasks = Task.objects.filter(user=user, course_id=course_id)
            total = tasks.count()
            completed = tasks.filter(status=Task.Status.COMPLETED).count()
            course = tasks.first().course if total else None
            payload.append(
                {
                    "course_id": str(course_id),
                    "course_code": getattr(course, "code", ""),
                    "course_name": getattr(course, "name", ""),
                    "completed": completed,
                    "total": total,
                    "percentage": round((completed / total) * 100, 2) if total else 0,
                }
            )
        return payload

    @staticmethod
    def streaks(user):
        dates = list(
            StudySession.objects.filter(user=user, completed=True, scheduled_start__isnull=False)
            .dates("scheduled_start", "day", order="DESC")
        )
        current_streak = 0
        longest_streak = 0
        previous_date = None
        for value in dates:
            if previous_date is None or previous_date - value == timedelta(days=1):
                current_streak += 1
            else:
                longest_streak = max(longest_streak, current_streak)
                current_streak = 1
            previous_date = value
        longest_streak = max(longest_streak, current_streak)
        return {"current_streak": current_streak, "longest_streak": longest_streak}
