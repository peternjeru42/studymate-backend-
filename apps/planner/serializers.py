from rest_framework import serializers

from apps.planner.models import AvailabilityBlock, PlanAdjustmentLog, PlanSource, StudyPlan, StudySession


class AvailabilityBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityBlock
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class PlanSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanSource
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class PlanAdjustmentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanAdjustmentLog
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class StudyPlanSerializer(serializers.ModelSerializer):
    study_sessions = StudySessionSerializer(many=True, read_only=True)
    plan_source = PlanSourceSerializer(read_only=True)
    adjustment_logs = PlanAdjustmentLogSerializer(many=True, read_only=True)

    class Meta:
        model = StudyPlan
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at", "is_saved", "applied_to_calendar")


class PlannerGenerateSerializer(serializers.Serializer):
    topic = serializers.CharField(required=False, allow_blank=True)
    deadline = serializers.DateTimeField(required=False)
    available_hours = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    difficulty = serializers.ChoiceField(choices=StudyPlan.Difficulty.choices, required=False)
    mode = serializers.ChoiceField(choices=StudyPlan.Mode.choices, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    task_id = serializers.UUIDField(required=False)
    assessment_id = serializers.UUIDField(required=False)
    course_id = serializers.UUIDField(required=False)
