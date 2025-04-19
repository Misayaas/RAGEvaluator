from django.test import TestCase
from prompt_eval.models.task import PromptTask

class TestPromptTask(TestCase):
    def test_task_creation(self):
        task = PromptTask.objects.create(
            name="测试任务"
        )
        self.assertEqual(task.name, "测试任务")