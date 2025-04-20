from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from prompt_eval.services.evaluator import PromptEvaluator
from prompt_eval.models.task import PromptTask
from prompt_eval.models.evaluation import PromptEvaluation
from langchain_core.runnables import Runnable

@override_settings(
    OPENAI_API_KEY='test_key_123456',
    OPENAI_API_BASE='test_base_url'
)
class TestPromptEvaluator(TestCase):
    @patch('prompt_eval.services.evaluator.ChatOpenAI')
    def setUp(self, mock_chat):
        mock_llm = MagicMock(spec=Runnable)
        mock_chat.return_value = mock_llm
        self.evaluator = PromptEvaluator()
        self.task = PromptTask.objects.create(
            name="测试任务"
        )

    @patch('prompt_eval.services.evaluator.ChatOpenAI')
    def test_create_task(self, mock_chat):
        task = self.evaluator.create_task(name="新测试任务")
        self.assertEqual(task.name, "新测试任务")

    # def test_create_and_evaluate(self):
    #     evaluation = self.evaluator.create_and_evaluate(
    #         task_id=self.task.id,
    #         prompt_text="测试prompt",
    #         model_name="test_model"
    #     )
    #     self.assertEqual(evaluation.task.id, self.task.id)
    #     self.assertEqual(evaluation.status, 'completed')

    @patch('prompt_eval.services.evaluator.ChatOpenAI')
    def test_get_task_evaluations(self, mock_chat):
        evaluation1 = PromptEvaluation.objects.create(
            task=self.task,
            prompt_text="测试prompt1",
            version=1
        )
        evaluation2 = PromptEvaluation.objects.create(
            task=self.task,
            prompt_text="测试prompt2",
            version=2
        )
        evaluations = self.evaluator.get_task_evaluations(self.task.id)
        self.assertEqual(len(evaluations), 2)