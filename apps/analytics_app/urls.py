from django.urls import path

from apps.analytics_app.views import AnalyticsCoursesAPIView, AnalyticsProgressAPIView, AnalyticsStreaksAPIView, DashboardAPIView

urlpatterns = [
    path("analytics/dashboard/", DashboardAPIView.as_view(), name="analytics-dashboard"),
    path("analytics/progress/", AnalyticsProgressAPIView.as_view(), name="analytics-progress"),
    path("analytics/courses/", AnalyticsCoursesAPIView.as_view(), name="analytics-courses"),
    path("analytics/streaks/", AnalyticsStreaksAPIView.as_view(), name="analytics-streaks"),
]
