from django.db import models
from .task import PromptTask

class CustomMetric(models.Model):
    task = models.ForeignKey(PromptTask, on_delete=models.CASCADE, related_name='custom_metrics', verbose_name="关联任务")
    name = models.CharField(max_length=100, verbose_name="指标名称")
    description = models.TextField(verbose_name="评估标准描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "自定义评估指标"
        verbose_name_plural = verbose_name
        unique_together = ('task', 'name')  