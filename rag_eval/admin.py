from django.contrib import admin

# Register yfrom django.contrib import admin
from .models.evaluation import RAGEvaluation, EvaluationResult
from .models.task import RAGTask

@admin.register(RAGTask)
class RAGTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    list_filter = ('name', 'created_at')


@admin.register(RAGEvaluation)
class RAGEvaluationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    list_filter = ('name', 'created_at')
    search_fields = ('name', 'created_at')


@admin.register(EvaluationResult)
class EvaluationResultAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'metric_name', 'metric_value')
    list_filter = ('metric_name',)
