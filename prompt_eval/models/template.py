# 定义Prompt模板的数据模型，支持版本管理和模板复用
from django.db import models
from django.contrib.auth.models import User

class PromptTemplate(models.Model):
    # 模板类型
    TEMPLATE_TYPES = [
        ('QA', '问答类'),
        ('SUMMARY', '摘要类'),
        ('ANALYSIS', '分析类'),
        ('CUSTOM', '自定义'),
    ]
    # 状态
    STATUS_CHOICES = [
        ('DRAFT', '草稿'),
        ('ACTIVE', '使用中'),
        ('ARCHIVED', '已归档'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="模板名称")
    description = models.TextField(verbose_name="模板描述", blank=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES, verbose_name="模板类型")
    content = models.TextField(verbose_name="模板内容")
    variables = models.JSONField(verbose_name="变量列表", default=dict)
    
    # 版本控制
    version = models.CharField(max_length=50, verbose_name="版本号")
    parent_version = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # 元数据
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 使用统计
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    avg_score = models.FloatField(default=0.0, verbose_name="平均评分")
    
    class Meta:
        db_table = 'prompt_template'
        ordering = ['-created_at']
        verbose_name = 'Prompt模板'
        verbose_name_plural = verbose_name
        unique_together = ('name', 'version')

    def __str__(self):
        return f"{self.name}-v{self.version}"
    
    # 创建新版本
    def create_new_version(self):
        """创建新版本的模板"""
        current_version = float(self.version)
        new_version = str(current_version + 0.1)
        
        new_template = PromptTemplate.objects.create(
            name=self.name,
            description=self.description,
            template_type=self.template_type,
            content=self.content,
            variables=self.variables,
            version=new_version,
            parent_version=self,
            created_by=self.created_by,
            status='DRAFT'
        )
        return new_template