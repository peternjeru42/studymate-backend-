from rest_framework import serializers

from apps.tasks.models import Task, TaskTag


class TaskTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTag
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class TaskSerializer(serializers.ModelSerializer):
    tags = TaskTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=TaskTag.objects.all(), write_only=True, required=False, source="tags"
    )
    effective_status = serializers.CharField(read_only=True)

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at", "completed_at")


class TaskRescheduleSerializer(serializers.Serializer):
    due_date = serializers.DateTimeField()
