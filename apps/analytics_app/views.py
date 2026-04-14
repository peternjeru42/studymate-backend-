from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.analytics_app.services import AnalyticsService
from apps.common.responses import api_response


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return api_response(data=AnalyticsService.dashboard(request.user))


class AnalyticsProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return api_response(data=AnalyticsService.progress(request.user))


class AnalyticsCoursesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return api_response(data=AnalyticsService.course_progress(request.user))


class AnalyticsStreaksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return api_response(data=AnalyticsService.streaks(request.user))
