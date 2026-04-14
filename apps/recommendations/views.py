from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.routers import DefaultRouter

from apps.common.responses import api_response
from apps.common.viewsets import UserOwnedModelViewSet
from apps.recommendations.models import Recommendation, RecommendationActionLog, RecommendationRule
from apps.recommendations.serializers import RecommendationRuleSerializer, RecommendationSerializer
from apps.recommendations.services import RecommendationEngine


class RecommendationViewSet(UserOwnedModelViewSet):
    queryset = Recommendation.objects.prefetch_related("action_logs").all()
    serializer_class = RecommendationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get("include_dismissed") != "true":
            queryset = queryset.filter(is_dismissed=False)
        urgency = self.request.query_params.get("urgency")
        category = self.request.query_params.get("category")
        if urgency:
            queryset = queryset.filter(urgency=urgency)
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class RecommendationRuleViewSet(viewsets.ModelViewSet):
    queryset = RecommendationRule.objects.all()
    serializer_class = RecommendationRuleSerializer


class RecommendationUrgentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        RecommendationEngine.sync_for_user(request.user)
        qs = Recommendation.objects.filter(user=request.user, is_dismissed=False, urgency__in=["high", "critical"])
        return api_response(data=RecommendationSerializer(qs, many=True).data)


class RecommendationApplyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        recommendation = get_object_or_404(Recommendation, user=request.user, pk=pk)
        recommendation.is_applied = True
        recommendation.applied_at = timezone.now()
        recommendation.save(update_fields=["is_applied", "applied_at", "updated_at"])
        RecommendationActionLog.objects.create(
            user=request.user, recommendation=recommendation, action="apply", metadata=request.data
        )
        return api_response(data=RecommendationSerializer(recommendation).data, message="Recommendation applied.")


class RecommendationDismissAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        recommendation = get_object_or_404(Recommendation, user=request.user, pk=pk)
        recommendation.is_dismissed = True
        recommendation.dismissed_at = timezone.now()
        recommendation.save(update_fields=["is_dismissed", "dismissed_at", "updated_at"])
        RecommendationActionLog.objects.create(
            user=request.user, recommendation=recommendation, action="dismiss", metadata=request.data
        )
        return api_response(data=RecommendationSerializer(recommendation).data, message="Recommendation dismissed.")


router = DefaultRouter()
router.register("recommendations", RecommendationViewSet, basename="recommendation")
router.register("recommendation-rules", RecommendationRuleViewSet, basename="recommendation-rule")

urlpatterns = [
    path("recommendations/urgent/", RecommendationUrgentAPIView.as_view(), name="recommendations-urgent"),
    path("recommendations/<uuid:pk>/apply/", RecommendationApplyAPIView.as_view(), name="recommendation-apply"),
    path("recommendations/<uuid:pk>/dismiss/", RecommendationDismissAPIView.as_view(), name="recommendation-dismiss"),
] + router.urls
