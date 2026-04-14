from datetime import datetime, time, timedelta

from django.urls import path
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.routers import DefaultRouter

from apps.calendar_app.models import CalendarEvent, FreeTimeWindow
from apps.calendar_app.serializers import CalendarEventSerializer, FreeTimeWindowSerializer
from apps.common.responses import api_response
from apps.common.viewsets import UserOwnedModelViewSet


class CalendarEventViewSet(UserOwnedModelViewSet):
    queryset = CalendarEvent.objects.prefetch_related("reminders").all()
    serializer_class = CalendarEventSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if start:
            queryset = queryset.filter(end_time__gte=start)
        if end:
            queryset = queryset.filter(start_time__lte=end)
        return queryset


class FreeTimeWindowViewSet(UserOwnedModelViewSet):
    queryset = FreeTimeWindow.objects.all()
    serializer_class = FreeTimeWindowSerializer


class CalendarDayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        target_date = (
            datetime.fromisoformat(request.query_params["date"]).date()
            if request.query_params.get("date")
            else timezone.now().date()
        )
        start = timezone.make_aware(datetime.combine(target_date, time.min))
        end = start + timedelta(days=1)
        events = CalendarEvent.objects.filter(user=request.user, start_time__lt=end, end_time__gte=start)
        return api_response(data=CalendarEventSerializer(events, many=True).data)


class CalendarWeekAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = (
            datetime.fromisoformat(request.query_params["start"]).date()
            if request.query_params.get("start")
            else timezone.now().date()
        )
        start = timezone.make_aware(datetime.combine(start_date, time.min))
        end = start + timedelta(days=7)
        events = CalendarEvent.objects.filter(user=request.user, start_time__lt=end, end_time__gte=start)
        return api_response(data=CalendarEventSerializer(events, many=True).data)


router = DefaultRouter()
router.register("calendar/events", CalendarEventViewSet, basename="calendar-event")
router.register("calendar/free-time", FreeTimeWindowViewSet, basename="free-time-window")

urlpatterns = router.urls + [
    path("calendar/day/", CalendarDayAPIView.as_view(), name="calendar-day"),
    path("calendar/week/", CalendarWeekAPIView.as_view(), name="calendar-week"),
]
