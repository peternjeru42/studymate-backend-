from rest_framework import serializers

from apps.assessments.models import Assessment, AssessmentPreparationStatus, AssessmentTopic


class AssessmentTopicSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source="topic.title", read_only=True)

    class Meta:
        model = AssessmentTopic
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class AssessmentPreparationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentPreparationStatus
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class AssessmentSerializer(serializers.ModelSerializer):
    assessment_topics = AssessmentTopicSerializer(many=True, read_only=True)
    topics = serializers.SerializerMethodField()
    preparation_status = AssessmentPreparationStatusSerializer(read_only=True)

    class Meta:
        model = Assessment
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def get_topics(self, obj):
        return [link.topic.title for link in obj.assessment_topics.select_related("topic").all()]
