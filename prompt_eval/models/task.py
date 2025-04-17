from django.db import models

# 定义prompt评估的任务模型
class PromptTask(models.Model):
    name = models.CharField(max_length=200, verbose_name="任务名称")
    description = models.TextField(verbose_name="任务描述", null=True, blank=True)
    goal = models.TextField(verbose_name="优化目标")
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', '进行中'),
            ('completed', '已完成'),
            ('archived', '已归档')
        ],
        default='active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'prompt_task'
        ordering = ['-created_at']
        verbose_name = 'Prompt任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"