from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.accounts.views import PreferencesAPIView, ProfileAPIView
from apps.analytics_app.views import DashboardAPIView
from apps.common.views import HealthCheckAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", HealthCheckAPIView.as_view(), name="health"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    path("api/v1/profile/", ProfileAPIView.as_view(), name="profile-direct"),
    path("api/v1/preferences/", PreferencesAPIView.as_view(), name="preferences-direct"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.academics.urls")),
    path("api/v1/", include("apps.tasks.urls")),
    path("api/v1/", include("apps.assessments.urls")),
    path("api/v1/", include("apps.planner.urls")),
    path("api/v1/", include("apps.recommendations.urls")),
    path("api/v1/", include("apps.calendar_app.urls")),
    path("api/v1/", include("apps.notifications.urls")),
    path("api/v1/", include("apps.analytics_app.urls")),
]
