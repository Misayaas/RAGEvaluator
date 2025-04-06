from ..models.evaluation import PromptEvaluation, EvaluationMetric
from ..models.template import PromptTemplate
import time
import uuid

class PromptEvaluator:
    def __init__(self):
        self.batch_id = str(uuid.uuid4())

    def evaluate_prompt(self, template_id, prompt_text, response, context, model_name):
        start_time = time.time()
        
        template = PromptTemplate.objects.get(id=template_id)
        
        # 创建评估记录
        evaluation = PromptEvaluation.objects.create(
            template=template,
            prompt_text=prompt_text,
            response=response,
            context=context,
            model_name=model_name,
            batch_id=self.batch_id,
            response_time=(time.time() - start_time) * 1000
        )
        
        # 计算评估指标
        metrics = self._calculate_metrics(prompt_text, response, context)
        
        # 更新评估记录
        evaluation.relevance_score = metrics['relevance']
        evaluation.coherence_score = metrics['coherence']
        evaluation.save()
        
        # 保存详细指标
        self._save_detailed_metrics(evaluation, metrics)
        
        return evaluation

    def _calculate_metrics(self, prompt, response, context):
        # 在这里实现具体的评估指标计算逻辑
        return {
            'relevance': 0.8,  # 示例值
            'coherence': 0.7,
            'completeness': 0.9,
            'token_efficiency': 0.85
        }

    def _save_detailed_metrics(self, evaluation, metrics):
        for name, value in metrics.items():
            EvaluationMetric.objects.create(
                evaluation=evaluation,
                metric_name=name,
                metric_value=value
            )