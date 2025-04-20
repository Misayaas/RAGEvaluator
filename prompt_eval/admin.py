from django.contrib import admin
from .models.evaluation import PromptEvaluation, EvaluationMetric
from .models.template import PromptTemplate

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'template_type', 'status', 'created_at', 'usage_count')
    list_filter = ('template_type', 'status', 'created_at')
    search_fields = ('name', 'description', 'content')

@admin.register(PromptEvaluation)
class PromptEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'prompt_text', 
        'model_name',
        'status',
        'faithfulness_score',
        'context_recall_score',
        'answer_relevancy_score',
        'context_precision_score',
        'created_at',
        'updated_at'
    )
    list_filter = ('model_name', 'status', 'created_at')
    search_fields = ('prompt_text', 'response', 'context')
    readonly_fields = (
        'faithfulness_score',
        'context_recall_score',
        'answer_relevancy_score',
        'context_precision_score',
        'version'
    )

@admin.register(EvaluationMetric)
class EvaluationMetricAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'metric_name', 'metric_value')
    list_filter = ('metric_name', 'evaluation')
    search_fields = ('metric_name',)
