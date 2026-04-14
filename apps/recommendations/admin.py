from django.contrib import admin

from apps.recommendations.models import Recommendation, RecommendationActionLog, RecommendationRule

admin.site.register(Recommendation)
admin.site.register(RecommendationRule)
admin.site.register(RecommendationActionLog)
