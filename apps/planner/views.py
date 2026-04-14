from django.shortcuts import get_object_or_404
from django.urls import path
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.routers import DefaultRouter

from apps.common.responses import api_response
from apps.common.viewsets import UserOwnedModelViewSet
from apps.planner.models import AvailabilityBlock, StudyPlan
from apps.planner.serializers import AvailabilityBlockSerializer, PlannerGenerateSerializer, StudyPlanSerializer
from apps.planner.services import PlannerOrchestratorService


class AvailabilityBlockViewSet(UserOwnedModelViewSet):
    queryset = AvailabilityBlock.objects.all()
    serializer_class = AvailabilityBlockSerializer


class StudyPlanViewSet(UserOwnedModelViewSet):
    queryset = StudyPlan.objects.prefetch_related("study_sessions", "adjustment_logs").all()
    serializer_class = StudyPlanSerializer


class PlannerGenerateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PlannerGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = PlannerOrchestratorService.generate_plan(user=request.user, validated_data=serializer.validated_data)
        return api_response(
            data=StudyPlanSerializer(plan).data,
            message="Study plan generated successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class PlannerRegenerateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("plan_id")
        plan = get_object_or_404(StudyPlan, user=request.user, id=plan_id)
        new_plan = PlannerOrchestratorService.regenerate_plan(user=request.user, plan=plan)
        return api_response(data=StudyPlanSerializer(new_plan).data, message="Study plan regenerated successfully.")


class StudyPlanSaveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        plan = get_object_or_404(StudyPlan, user=request.user, id=pk)
        plan.is_saved = True
        plan.save(update_fields=["is_saved", "updated_at"])
        return api_response(data=StudyPlanSerializer(plan).data, message="Study plan saved successfully.")


class StudyPlanApplyToCalendarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        plan = get_object_or_404(StudyPlan.objects.prefetch_related("study_sessions"), user=request.user, id=pk)
        events = PlannerOrchestratorService.apply_to_calendar(user=request.user, plan=plan)
        return api_response(
            data={"created_events": [str(event.id) for event in events]},
            message="Study plan applied to calendar.",
        )


class StudyPlanConvertToTasksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        plan = get_object_or_404(StudyPlan.objects.prefetch_related("study_sessions"), user=request.user, id=pk)
        tasks = PlannerOrchestratorService.convert_to_tasks(user=request.user, plan=plan)
        return api_response(
            data={"created_tasks": [str(task.id) for task in tasks]},
            message="Study sessions converted to tasks.",
        )


router = DefaultRouter()
router.register("planner/plans", StudyPlanViewSet, basename="planner-plan")
router.register("planner/availability", AvailabilityBlockViewSet, basename="availability-block")

urlpatterns = router.urls + [
    path("planner/generate/", PlannerGenerateAPIView.as_view(), name="planner-generate"),
    path("planner/regenerate/", PlannerRegenerateAPIView.as_view(), name="planner-regenerate"),
    path("planner/plans/<uuid:pk>/save/", StudyPlanSaveAPIView.as_view(), name="planner-save"),
    path(
        "planner/plans/<uuid:pk>/apply-to-calendar/",
        StudyPlanApplyToCalendarAPIView.as_view(),
        name="planner-apply-to-calendar",
    ),
    path(
        "planner/plans/<uuid:pk>/convert-to-tasks/",
        StudyPlanConvertToTasksAPIView.as_view(),
        name="planner-convert-to-tasks",
    ),
]
