from django.db import models

# 定义rag评估的任务模型
class RAGTask(models.Model):
    name = models.CharField(max_length=200, verbose_name="任务名称")
    description = models.TextField(verbose_name="任务描述")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'rag_task'
        ordering = ['-created_at']
        verbose_name = 'RAG任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"
