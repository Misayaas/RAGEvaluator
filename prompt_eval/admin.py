from django.contrib import admin
from .models.evaluation import PromptEvaluation, EvaluationMetric
from .models.template import PromptTemplate
from .models.evaluation import AspectMetric

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'content')

@admin.register(PromptTask)
class PromptTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')

@admin.register(PromptEvaluation)
class PromptEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'prompt_text', 
        'model_name',
        'status',
        'faithfulness_score',
        'relevance_score',
        'coherence_score',
        'helpfulness_score',
        'created_at',
        'updated_at'
    )
    list_filter = ('model_name', 'status', 'created_at')
    search_fields = ('prompt_text', 'response', 'context')
    readonly_fields = (
        'faithfulness_score',
        'relevance_score',
        'coherence_score',
        'helpfulness_score',
        'version'
    )

@admin.register(EvaluationMetric)
class EvaluationMetricAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'metric_name', 'metric_value')
    list_filter = ('metric_name', 'evaluation')
    search_fields = ('metric_name',)


@admin.register(AspectMetric)
class AspectMetricAdmin(admin.ModelAdmin):
    list_display = ('name', 'task', 'description', 'created_at')
    list_filter = ('task', 'created_at')
    search_fields = ('name', 'description')
