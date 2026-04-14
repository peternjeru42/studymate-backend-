from rest_framework import filters

from apps.academics.models import Course, Enrollment, Semester, Subtopic, Topic
from apps.academics.serializers import (
    CourseSerializer,
    EnrollmentSerializer,
    SemesterSerializer,
    SubtopicSerializer,
    TopicSerializer,
)
from apps.common.viewsets import UserOwnedModelViewSet


class SemesterViewSet(UserOwnedModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class CourseViewSet(UserOwnedModelViewSet):
    queryset = Course.objects.select_related("semester").all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["code", "name", "instructor"]


class EnrollmentViewSet(UserOwnedModelViewSet):
    queryset = Enrollment.objects.select_related("course").all()
    serializer_class = EnrollmentSerializer


class TopicViewSet(UserOwnedModelViewSet):
    queryset = Topic.objects.select_related("course").all()
    serializer_class = TopicSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]

    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset


class SubtopicViewSet(UserOwnedModelViewSet):
    queryset = Subtopic.objects.select_related("topic").all()
    serializer_class = SubtopicSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        topic_id = self.request.query_params.get("topic")
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        return queryset
