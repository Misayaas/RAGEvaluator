# 定义Prompt模板的数据模型，支持版本管理和模板复用
from django.db import models
from django.contrib.auth.models import User

class PromptTemplate(models.Model):
    name = models.CharField(max_length=200, verbose_name="模板名称")
    content = models.TextField(verbose_name="模板内容")
    variables = models.JSONField(verbose_name="变量列表", default=list)
    
    class Meta:
        db_table = 'simple_prompt_template'
        verbose_name = '简化版Prompt模板'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name