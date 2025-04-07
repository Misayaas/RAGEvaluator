# rag的评估记录
from django.db import models

# rag评估模型
class RAGEvaluation(models.Model):
    # 基本信息
    name = models.TextField(verbose_name="评估任务名称")
    description = models.TextField(verbose_name="任务描述")
    query = models.TextField(verbose_name="查询内容")
    retrieved_docs = models.TextField(verbose_name="检索到的文档")
    generated_answer = models.TextField(verbose_name="生成的答案")
    
    # 评估指标
    faithfulness_score = models.FloatField(verbose_name="答案忠实度", default=0.0)
    answer_relevancy_score = models.FloatField(verbose_name="答案相关性", default=0.0)
    context_relevancy_score = models.FloatField(verbose_name="上下文相关性", default=0.0)
    context_precision_score = models.FloatField(verbose_name="上下文精确度", default=0.0)
    context_recall_score = models.FloatField(verbose_name="上下文召回率", default=0.0)
    response_time = models.FloatField(verbose_name="响应时间(ms)", default=0.0)
    
    # 元数据
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    # evaluated_file = models.TextField(verbose_name="被评估的数据文件")
    batch_id = models.CharField(max_length=50, verbose_name="批次ID")
    
    class Meta:
        db_table = 'rag_evaluation' # 数据库表名
        ordering = ['-created_at'] # 排序方式
        verbose_name = 'RAG评估记录' 
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Evaluation-{self.id}-{self.created_at.strftime('%Y%m%d')}"


# 存储评估指标的模型
class EvaluationResult(models.Model):
    evaluation = models.ForeignKey(RAGEvaluation, on_delete=models.CASCADE, related_name='detailed_metrics')
    metric_name = models.CharField(max_length=100, verbose_name="指标名称")
    metric_value = models.FloatField(verbose_name="指标值")
    metric_details = models.JSONField(verbose_name="详细信息", null=True, blank=True)
    
    class Meta:
        db_table = 'rag_evaluation_result'
        unique_together = ('evaluation', 'metric_name')# 存储RAG系统评估的结果和指标
