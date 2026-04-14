from django.shortcuts import get_object_or_404
from django.urls import path
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.routers import DefaultRouter

from apps.common.responses import api_response
from apps.common.viewsets import UserOwnedModelViewSet
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationViewSet(UserOwnedModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class NotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        notification = get_object_or_404(Notification, user=request.user, pk=pk)
        notification.read = True
        notification.save(update_fields=["read", "updated_at"])
        return api_response(data=NotificationSerializer(notification).data, message="Notification marked as read.")


class NotificationMarkAllReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return api_response(data=None, message="All notifications marked as read.")


router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("notifications/<uuid:pk>/read/", NotificationReadAPIView.as_view(), name="notification-read"),
    path("notifications/mark-all-read/", NotificationMarkAllReadAPIView.as_view(), name="notifications-mark-all-read"),
] + router.urls
