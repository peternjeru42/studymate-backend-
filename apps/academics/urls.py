from rest_framework.routers import DefaultRouter

from apps.academics.views import CourseViewSet, EnrollmentViewSet, SemesterViewSet, SubtopicViewSet, TopicViewSet

router = DefaultRouter()
router.register("semesters", SemesterViewSet, basename="semester")
router.register("courses", CourseViewSet, basename="course")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("topics", TopicViewSet, basename="topic")
router.register("subtopics", SubtopicViewSet, basename="subtopic")

urlpatterns = router.urls
