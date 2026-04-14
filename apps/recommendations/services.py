from django.utils import timezone

from apps.assessments.models import Assessment
from apps.recommendations.models import Recommendation
from apps.tasks.models import Task


class RecommendationEngine:
    @classmethod
    def sync_for_user(cls, user):
        Recommendation.objects.filter(user=user, is_dismissed=False, is_applied=False).delete()
        recommendations = []
        overdue_tasks = Task.objects.filter(user=user, due_date__lt=timezone.now()).exclude(status=Task.Status.COMPLETED)
        for task in overdue_tasks:
            recommendations.append(
                Recommendation(
                    user=user,
                    title=f"Overdue task: {task.title}",
                    description=f"{task.title} is overdue and needs immediate attention.",
                    urgency=Recommendation.Urgency.CRITICAL,
                    category=Recommendation.Category.DEADLINE_RISK,
                    suggested_action="Reschedule or complete this task today.",
                    action_type="reschedule",
                    related_item_type="task",
                    related_item_id=str(task.id),
                )
            )
        upcoming_assessments = Assessment.objects.filter(user=user, date__gte=timezone.now()).order_by("date")[:3]
        for assessment in upcoming_assessments:
            recommendations.append(
                Recommendation(
                    user=user,
                    title=f"Prepare for {assessment.title}",
                    description=f"{assessment.title} is coming up soon.",
                    urgency=Recommendation.Urgency.HIGH,
                    category=Recommendation.Category.WORKLOAD,
                    suggested_action="Generate a preparation plan and start the highest-value topics first.",
                    action_type="plan",
                    related_item_type="assessment",
                    related_item_id=str(assessment.id),
                )
            )
        Recommendation.objects.bulk_create(recommendations)
        return Recommendation.objects.filter(user=user)
