from rest_framework import serializers

from apps.recommendations.models import Recommendation, RecommendationActionLog, RecommendationRule


class RecommendationActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationActionLog
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class RecommendationSerializer(serializers.ModelSerializer):
    action_logs = RecommendationActionLogSerializer(many=True, read_only=True)

    class Meta:
        model = Recommendation
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at", "dismissed_at", "applied_at")


class RecommendationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationRule
        fields = "__all__"
