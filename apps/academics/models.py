from django.db import models

from apps.common.models import OwnedByUserModel, TimeStampedModel, UUIDPrimaryKeyModel


class Semester(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    name = models.CharField(max_length=120)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-is_active", "name")

    def __str__(self):
        return self.name


class Course(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    semester = models.ForeignKey(Semester, null=True, blank=True, on_delete=models.SET_NULL, related_name="courses")
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=255)
    instructor = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=32, default="bg-blue-500")
    credits = models.PositiveIntegerField(default=3)
    study_hours_per_week = models.PositiveIntegerField(default=5)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrollment(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, default="active")

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.email} -> {self.course.code}"


class Topic(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title


class Subtopic(UUIDPrimaryKeyModel, OwnedByUserModel, TimeStampedModel):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="subtopics")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title
