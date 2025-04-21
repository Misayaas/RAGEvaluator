from django.db import models
from .task import PromptTask
from .evaluation import PromptEvaluation

class CustomMetric(models.Model):
    task = models.ForeignKey(PromptTask, on_delete=models.CASCADE, related_name='custom_metrics', verbose_name="关联任务")
    name = models.CharField(max_length=100, verbose_name="指标名称")
    description = models.TextField(verbose_name="评估标准描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "自定义评估指标"
        verbose_name_plural = verbose_name
        unique_together = ('task', 'name')

class MetricScore(models.Model):
    """指标评分记录"""
    evaluation = models.ForeignKey(PromptEvaluation, on_delete=models.CASCADE, related_name='metric_scores', verbose_name="关联评估")
    metric = models.ForeignKey(CustomMetric, on_delete=models.CASCADE, related_name='scores', verbose_name="评估指标")
    score = models.FloatField(verbose_name="评分")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "指标评分"
        verbose_name_plural = verbose_name
        unique_together = ('evaluation', 'metric')

    def __str__(self):
        return f"{self.metric.name}: {self.score}"