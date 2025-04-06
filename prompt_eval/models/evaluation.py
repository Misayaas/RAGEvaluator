# prompts的评估记录
from django.db import models
from .template import PromptTemplate

# prompt评估模型
class PromptEvaluation(models.Model):
    # 基本信息
    template = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE, related_name='evaluations')
    prompt_text = models.TextField(verbose_name="实际使用的Prompt")
    response = models.TextField(verbose_name="模型响应")
    context = models.TextField(verbose_name="上下文信息")
    
    # 评估指标
    relevance_score = models.FloatField(verbose_name="相关性得分", default=0.0)
    coherence_score = models.FloatField(verbose_name="连贯性得分", default=0.0)
    response_time = models.FloatField(verbose_name="响应时间(ms)", default=0.0)
    token_count = models.IntegerField(verbose_name="Token数量", default=0)
    
    # 元数据
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    model_name = models.CharField(max_length=100, verbose_name="评估使用的模型")
    batch_id = models.CharField(max_length=50, verbose_name="批次ID")
    
    class Meta:
        db_table = 'prompt_evaluation' # 数据库表名
        ordering = ['-created_at'] # 排序方式
        verbose_name = 'Prompt评估记录' 
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Evaluation-{self.id}-{self.created_at.strftime('%Y%m%d')}"


# 存储评估指标的模型
class EvaluationMetric(models.Model):
    evaluation = models.ForeignKey(PromptEvaluation, on_delete=models.CASCADE, related_name='detailed_metrics')
    metric_name = models.CharField(max_length=100, verbose_name="指标名称")
    metric_value = models.FloatField(verbose_name="指标值")
    metric_details = models.JSONField(verbose_name="详细信息", null=True, blank=True)
    
    class Meta:
        db_table = 'evaluation_metric'
        unique_together = ('evaluation', 'metric_name')