from django.db import models
from django.core.exceptions import ValidationError

class PromptEvaluation(models.Model):
    # 基本信息
    prompt_text = models.TextField(verbose_name="实际使用的Prompt")
    response = models.TextField(verbose_name="模型响应", null=True, blank=True)
    context = models.TextField(verbose_name="上下文信息", null=True, blank=True)
    
    # Ragas 评估指标
    # faithfulness_score = models.FloatField(verbose_name="忠实度", default=0.0)
    # context_recall_score = models.FloatField(verbose_name="上下文召回率", default=0.0)
    answer_relevancy_score = models.FloatField(verbose_name="答案相关性", default=0.0)
    # context_precision_score = models.FloatField(verbose_name="上下文精确度", default=0.0)
    
    # 状态跟踪
    status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', '等待响应'),
            ('responded', '已获得响应'),
            ('evaluating', '评估中'),
            ('completed', '评估完成'),
            ('failed', '评估失败')
        ],
        default='pending'
    )
    
    # 版本控制
    version = models.IntegerField(verbose_name="版本号", default=1)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='iterations')
    
    # 元数据
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    model_name = models.CharField(max_length=100, verbose_name="评估使用的模型")
    
    class Meta:
        db_table = 'prompt_evaluation'
        ordering = ['-created_at']
        verbose_name = 'Prompt评估记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Evaluation-{self.id}-v{self.version}"

    def update_response(self, response_text):
        """更新模型响应"""
        self.response = response_text
        self.status = 'responded'
        self.save()
        return self

    def create_next_version(self, new_prompt_text):
        """创建下一个版本的评估"""
        if self.status not in ['completed', 'failed']:
            raise ValidationError("只能基于已完成或失败的评估创建新版本")
        
        return PromptEvaluation.objects.create(
            prompt_text=new_prompt_text,
            context=self.context,
            version=self.version + 1,
            parent=self,
            model_name=self.model_name
        )

class EvaluationMetric(models.Model):
    evaluation = models.ForeignKey(PromptEvaluation, on_delete=models.CASCADE, related_name='detailed_metrics')
    metric_name = models.CharField(max_length=100, verbose_name="指标名称")
    metric_value = models.FloatField(verbose_name="指标值")
    metric_details = models.JSONField(verbose_name="详细信息", null=True, blank=True)
    
    class Meta:
        db_table = 'evaluation_metric'
        unique_together = ('evaluation', 'metric_name')
