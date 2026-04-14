from rest_framework import serializers

from apps.academics.models import Course, Enrollment, Semester, Subtopic, Topic


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class EnrollmentSerializer(serializers.ModelSerializer):
    course_detail = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")


class SubtopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtopic
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")
