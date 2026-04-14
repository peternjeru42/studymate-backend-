from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.responses import api_response


class HealthCheckAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return api_response(
            data={"status": "ok", "time": timezone.now()},
            message="StudyMate backend is healthy",
        )
