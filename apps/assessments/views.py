from rest_framework.decorators import action
from rest_framework import filters

from apps.assessments.models import Assessment, AssessmentPreparationStatus, AssessmentTopic
from apps.assessments.serializers import (
    AssessmentPreparationStatusSerializer,
    AssessmentSerializer,
    AssessmentTopicSerializer,
)
from apps.common.responses import api_response
from apps.common.viewsets import UserOwnedModelViewSet


class AssessmentViewSet(UserOwnedModelViewSet):
    queryset = Assessment.objects.select_related("course").prefetch_related("assessment_topics__topic").all()
    serializer_class = AssessmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "course__code", "course__name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get("course")
        assessment_type = self.request.query_params.get("type")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if assessment_type:
            queryset = queryset.filter(type=assessment_type)
        return queryset

    @action(detail=True, methods=["post"])
    def generate_prep_plan(self, request, pk=None):
        assessment = self.get_object()
        payload = {
            "assessment_id": str(assessment.id),
            "title": assessment.title,
            "course_id": str(assessment.course_id),
            "date": assessment.date,
            "estimated_study_hours": assessment.estimated_study_hours,
            "topics": [link.topic.title for link in assessment.assessment_topics.select_related("topic").all()],
        }
        return api_response(data=payload, message="Assessment prep context generated.")


class AssessmentTopicViewSet(UserOwnedModelViewSet):
    queryset = AssessmentTopic.objects.select_related("assessment", "topic").all()
    serializer_class = AssessmentTopicSerializer


class AssessmentPreparationStatusViewSet(UserOwnedModelViewSet):
    queryset = AssessmentPreparationStatus.objects.select_related("assessment").all()
    serializer_class = AssessmentPreparationStatusSerializer
