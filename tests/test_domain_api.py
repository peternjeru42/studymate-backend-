from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.academics.models import Course
from apps.notifications.models import Notification
from apps.tasks.models import Task


@pytest.mark.django_db
def test_task_complete_and_reschedule(auth_client):
    course_response = auth_client.post(
        "/api/v1/courses/",
        {
            "code": "CS401",
            "name": "Data Structures",
            "instructor": "Dr. J",
            "credits": 4,
            "study_hours_per_week": 8,
        },
        format="json",
    )
    assert course_response.status_code == 201
    course_id = course_response.json()["id"]

    task_response = auth_client.post(
        "/api/v1/tasks/",
        {
            "course": course_id,
            "title": "Binary tree assignment",
            "type": "assignment",
            "due_date": (timezone.now() + timedelta(days=2)).isoformat(),
            "priority": "high",
            "status": "not-started",
            "estimated_hours": "4.00",
        },
        format="json",
    )
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    complete_response = auth_client.post(f"/api/v1/tasks/{task_id}/complete/", format="json")
    assert complete_response.status_code == 200
    assert complete_response.json()["data"]["status"] == "completed"

    reschedule_response = auth_client.post(
        f"/api/v1/tasks/{task_id}/reschedule/",
        {"due_date": (timezone.now() + timedelta(days=5)).isoformat()},
        format="json",
    )
    assert reschedule_response.status_code == 200


@pytest.mark.django_db
def test_planner_generate_apply_calendar_and_convert_tasks(auth_client):
    me = auth_client.get("/api/v1/auth/profile/").json()["data"]
    course = Course.objects.create(
        user_id=me["id"],
        code="MATH301",
        name="Discrete Math",
        instructor="Prof. Chen",
        credits=3,
        study_hours_per_week=6,
    )

    with patch("apps.ai_engine.services.OpenAIResponseService.generate_json") as mock_generate:
        mock_generate.return_value = {
            "study_sessions": [
                {
                    "day_number": 1,
                    "topic": "Graph Theory Foundations",
                    "focus_areas": ["graphs", "terminology", "representations"],
                    "estimated_time": 2,
                    "learning_method": "active-recall",
                    "notes": "Learn the core graph definitions first.",
                },
                {
                    "day_number": 2,
                    "topic": "Traversal and Practice",
                    "focus_areas": ["BFS", "DFS", "practice questions"],
                    "estimated_time": 4,
                    "learning_method": "practice-problems",
                    "notes": "Solve a mixed set of traversal problems.",
                },
            ],
            "revision_milestones": [
                {
                    "day": 2,
                    "milestone": "Complete the first full practice round.",
                    "review_topics": ["graphs", "BFS", "DFS"],
                }
            ],
            "retention_tips": [
                "Summarize each traversal method in your own words.",
                "Redo one problem from memory after every session.",
            ],
            "risk_alerts": ["The deadline is close, so keep sessions focused and avoid context switching."],
        }

        generate_response = auth_client.post(
            "/api/v1/planner/generate/",
            {
                "topic": "Graph Theory",
                "deadline": (timezone.now() + timedelta(days=2)).isoformat(),
                "available_hours": "6.00",
                "difficulty": "hard",
                "mode": "exam-prep",
                "course_id": str(course.id),
            },
            format="json",
        )
    assert generate_response.status_code == 201
    plan = generate_response.json()["data"]
    assert len(plan["study_sessions"]) >= 1

    apply_response = auth_client.post(f"/api/v1/planner/plans/{plan['id']}/apply-to-calendar/", format="json")
    assert apply_response.status_code == 200
    assert len(apply_response.json()["data"]["created_events"]) >= 1

    convert_response = auth_client.post(f"/api/v1/planner/plans/{plan['id']}/convert-to-tasks/", format="json")
    assert convert_response.status_code == 200
    assert len(convert_response.json()["data"]["created_tasks"]) >= 1

    notifications = Notification.objects.count()
    assert notifications >= 1


@pytest.mark.django_db
def test_planner_generate_requires_openai_config(auth_client):
    response = auth_client.post(
        "/api/v1/planner/generate/",
        {
            "topic": "Operating Systems",
            "deadline": (timezone.now() + timedelta(days=3)).isoformat(),
            "available_hours": "4.00",
            "difficulty": "medium",
            "mode": "deep-study",
        },
        format="json",
    )

    assert response.status_code == 503
    assert response.json()["error"] == "OPENAI_API_KEY is not configured on the Railway backend."


@pytest.mark.django_db
def test_dashboard_and_recommendations(auth_client):
    me = auth_client.get("/api/v1/auth/profile/").json()["data"]
    user_id = me["id"]
    course = Course.objects.create(
        user_id=user_id,
        code="ENG201",
        name="Literature",
        instructor="Dr. W",
        credits=3,
        study_hours_per_week=4,
    )
    Task.objects.create(
        user_id=user_id,
        course=course,
        title="Overdue essay",
        type="assignment",
        due_date=timezone.now() - timedelta(days=1),
        priority="critical",
        status="not-started",
        estimated_hours="3.00",
    )

    urgent_response = auth_client.get("/api/v1/recommendations/urgent/")
    assert urgent_response.status_code == 200
    assert len(urgent_response.json()["data"]) >= 1

    dashboard_response = auth_client.get("/api/v1/dashboard/")
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()["data"]
    assert dashboard["unread_notifications_count"] >= 0
