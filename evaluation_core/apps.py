## 应用的配置类，包含应用的基本信息
from django.apps import AppConfig


class EvaluationCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "evaluation_core"
