from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from prompt_eval.models.task import PromptTask
from prompt_eval.models.evaluation import PromptEvaluation
from langchain_core.runnables import Runnable

@override_settings(
    OPENAI_API_KEY='test_key_123456',
    OPENAI_API_BASE='test_base_url'
)
class TestPromptEvaluationViewSet(APITestCase):
    def setUp(self):
        self.task = PromptTask.objects.create(
            name="测试任务"
        )
        self.evaluation = PromptEvaluation.objects.create(
            task=self.task,
            prompt_text="测试prompt"
        )

    @patch('prompt_eval.services.evaluator.ChatOpenAI')
    def test_create_task(self, mock_chat):
        # 创建模拟的 Runnable 对象
        mock_llm = MagicMock(spec=Runnable)
        mock_chat.return_value = mock_llm
        
        url = reverse('evaluations-create-task')
        data = {
            'name': '新测试任务',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('task_id', response.data)

    @patch('prompt_eval.services.evaluator.ChatOpenAI')
    def test_task_evaluations(self, mock_chat ):
        # 创建模拟的 Runnable 对象
        mock_llm = MagicMock(spec=Runnable)
        mock_chat.return_value = mock_llm
        
        url = reverse('evaluations-task-evaluations', kwargs={'pk': self.task.id}) 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)