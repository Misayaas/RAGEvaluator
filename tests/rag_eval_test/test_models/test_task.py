from django.test import TestCase
from rag_eval.models.task import RAGTask

class TestEvaluationTask(TestCase):
    def test_task_creation(self):
        task = RAGTask.objects.create(
            name="测试任务",
            description="测试任务",
        )
        self.assertEqual(task.name, "测试任务")
