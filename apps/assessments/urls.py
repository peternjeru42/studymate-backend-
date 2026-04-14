from rest_framework.routers import DefaultRouter

from apps.assessments.views import AssessmentPreparationStatusViewSet, AssessmentTopicViewSet, AssessmentViewSet

router = DefaultRouter()
router.register("assessments", AssessmentViewSet, basename="assessment")
router.register("assessment-topics", AssessmentTopicViewSet, basename="assessment-topic")
router.register("assessment-preparation-statuses", AssessmentPreparationStatusViewSet, basename="assessment-preparation-status")

urlpatterns = router.urls
