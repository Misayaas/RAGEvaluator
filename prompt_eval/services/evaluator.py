from ragas import evaluate
from ragas.metrics import faithfulness, context_recall, answer_relevancy, context_precision
from ..models.evaluation import PromptEvaluation, EvaluationMetric
from django.core.exceptions import ValidationError
import time

class PromptEvaluator:
    def __init__(self):
        self.metrics = [
            faithfulness,
            context_recall,
            answer_relevancy,
            context_precision
        ]

    def create_evaluation(self, prompt_text, context=None, model_name="default"):
        """创建新的评估任务"""
        return PromptEvaluation.objects.create(
            prompt_text=prompt_text,
            context=context,
            model_name=model_name,
            status='pending'
        )

    def update_response(self, evaluation_id, response_text):
        """更新模型响应并开始评估"""
        try:
            evaluation = PromptEvaluation.objects.get(id=evaluation_id)
            evaluation.update_response(response_text)
            return self.evaluate_prompt(evaluation)
        except PromptEvaluation.DoesNotExist:
            raise ValidationError(f"未找到ID为{evaluation_id}的评估记录")

    def evaluate_prompt(self, evaluation):
        """评估一个prompt"""
        if evaluation.status != 'responded':
            raise ValidationError("只能评估已有响应的记录")

        try:
            evaluation.status = 'evaluating'
            evaluation.save()
            
            # 计算评估指标
            metrics = self._calculate_metrics(
                evaluation.prompt_text,
                evaluation.response,
                evaluation.context
            )
            
            # 更新评估记录
            evaluation.faithfulness_score = metrics.get('faithfulness', 0.0)
            evaluation.context_recall_score = metrics.get('context_recall', 0.0)
            evaluation.answer_relevancy_score = metrics.get('answer_relevancy', 0.0)
            evaluation.context_precision_score = metrics.get('context_precision', 0.0)
            evaluation.status = 'completed'
            evaluation.save()
            
            # 保存详细指标
            self._save_detailed_metrics(evaluation, metrics)
            
            return evaluation
            
        except Exception as e:
            evaluation.status = 'failed'
            evaluation.save()
            raise ValidationError(f"评估过程出现错误: {str(e)}")

    def create_next_version(self, evaluation_id, new_prompt_text):
        """创建新版本的评估"""
        try:
            evaluation = PromptEvaluation.objects.get(id=evaluation_id)
            return evaluation.create_next_version(new_prompt_text)
        except PromptEvaluation.DoesNotExist:
            raise ValidationError(f"未找到ID为{evaluation_id}的评估记录")

    def get_evaluation_history(self, evaluation_id):
        """获取评估历史记录"""
        try:
            evaluation = PromptEvaluation.objects.get(id=evaluation_id)
            history = []
            
            # 获取所有前代版本
            current = evaluation
            while current.parent:
                history.append(current.parent)
                current = current.parent
                
            return history
        except PromptEvaluation.DoesNotExist:
            raise ValidationError(f"未找到ID为{evaluation_id}的评估记录")

    def _calculate_metrics(self, prompt, response, context):
        """计算各项评估指标"""
        try:
            # 使用 Ragas 评估
            scores = evaluate(
                dataset={
                    "question": [prompt],
                    "answer": [response] if response else [],
                    "context": [[context]] if context else [],
                },
                metrics=self.metrics
            )
            
            return {
                'faithfulness': float(scores['faithfulness']),
                'context_recall': float(scores['context_recall']),
                'answer_relevancy': float(scores['answer_relevancy']),
                'context_precision': float(scores['context_precision'])
            }
            
        except Exception as e:
            raise ValidationError(f"指标计算错误: {str(e)}")

    def _save_detailed_metrics(self, evaluation, metrics):
        """保存详细评估指标"""
        for name, value in metrics.items():
            EvaluationMetric.objects.create(
                evaluation=evaluation,
                metric_name=name,
                metric_value=value
            )