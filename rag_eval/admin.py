from django.contrib import admin

# Register yfrom django.contrib import admin
from .models.evaluation import RAGEvaluation, EvaluationResult

@admin.register()
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'template_type', 'status', 'created_at', 'usage_count')
    list_filter = ('template_type', 'status', 'created_at')
    search_fields = ('name', 'description', 'content')

@admin.register(RAGEvaluation)
class PromptEvaluationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'evaluated_file', 'created_at')
    list_filter = ('name', 'created_at')
    search_fields = ('name', 'created_at')

@admin.register(EvaluationResult)
class EvaluationMetricAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'metric_name', 'metric_value')
    list_filter = ('metric_name',)
