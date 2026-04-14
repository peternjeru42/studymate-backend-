from django.utils import timezone
from rest_framework.decorators import action
from rest_framework import filters, status

from apps.common.responses import api_response
from apps.common.viewsets import UserOwnedModelViewSet
from apps.tasks.models import Task, TaskTag
from apps.tasks.serializers import TaskRescheduleSerializer, TaskSerializer, TaskTagSerializer


class TaskTagViewSet(UserOwnedModelViewSet):
    queryset = TaskTag.objects.all()
    serializer_class = TaskTagSerializer


class TaskViewSet(UserOwnedModelViewSet):
    queryset = Task.objects.select_related("course").prefetch_related("tags").all()
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description", "notes"]

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get("course")
        status_value = self.request.query_params.get("status")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if status_value:
            if status_value == Task.Status.OVERDUE:
                queryset = queryset.filter(due_date__lt=timezone.now()).exclude(status=Task.Status.COMPLETED)
            else:
                queryset = queryset.filter(status=status_value)
        return queryset

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = Task.Status.COMPLETED
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at", "updated_at"])
        return api_response(data=TaskSerializer(task).data, message="Task completed successfully.")

    @action(detail=True, methods=["post"], serializer_class=TaskRescheduleSerializer)
    def reschedule(self, request, pk=None):
        task = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task.due_date = serializer.validated_data["due_date"]
        if task.status == Task.Status.OVERDUE:
            task.status = Task.Status.NOT_STARTED
        task.save()
        return api_response(data=TaskSerializer(task).data, message="Task rescheduled successfully.")
