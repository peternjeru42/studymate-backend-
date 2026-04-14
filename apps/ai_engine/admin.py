from django.contrib import admin

from apps.ai_engine.models import AIRequestLog, AIResponseLog, PlanGenerationContext, PromptTemplate

admin.site.register(PromptTemplate)
admin.site.register(PlanGenerationContext)
admin.site.register(AIRequestLog)
admin.site.register(AIResponseLog)
