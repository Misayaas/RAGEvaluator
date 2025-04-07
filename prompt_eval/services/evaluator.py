from langchain.evaluation import load_evaluator, EvaluatorType
from ..models.evaluation import PromptEvaluation, EvaluationMetric
from ..models.template import PromptTemplate
import time
import uuid

class PromptEvaluator:
    def __init__(self):
        self.batch_id = str(uuid.uuid4())
        # 初始化各个评估器
        self.criteria_evaluator = load_evaluator(EvaluatorType.CRITERIA)
        self.qa_evaluator = load_evaluator(EvaluatorType.QA)
        self.helpfulness_evaluator = load_evaluator(EvaluatorType.LABELED_CRITERIA, criteria="helpfulness")
        self.correctness_evaluator = load_evaluator(EvaluatorType.LABELED_CRITERIA, criteria="correctness")
        self.relevance_evaluator = load_evaluator(EvaluatorType.LABELED_CRITERIA, criteria="relevance")
        self.coherence_evaluator = load_evaluator(EvaluatorType.LABELED_CRITERIA, criteria="coherence")

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
        evaluation.criteria_score = metrics['criteria']
        evaluation.qa_relevance_score = metrics['qa_relevance']
        evaluation.helpfulness_score = metrics['helpfulness']
        evaluation.correctness_score = metrics['correctness']
        evaluation.relevance_score = metrics['relevance']
        evaluation.coherence_score = metrics['coherence']
        evaluation.save()
        
        # 保存详细指标
        self._save_detailed_metrics(evaluation, metrics)
        
        return evaluation

    # 评估指标计算逻辑
    def _calculate_metrics(self, prompt, response, context):
        try:
            # 使用各个评估器进行评估
            metrics = {
                'criteria': float(self.criteria_evaluator.evaluate_strings(prediction=response,input=prompt)['score']),
                'qa_relevance': float(self.qa_evaluator.evaluate_strings(prediction=response,input=prompt,reference=context)['score']),
                'helpfulness': float(self.helpfulness_evaluator.evaluate_strings(prediction=response,input=prompt)['score']),
                'correctness': float(self.correctness_evaluator.evaluate_strings(prediction=response,input=prompt)['score']),
                'relevance': float(self.relevance_evaluator.evaluate_strings(prediction=response,input=prompt)['score']),
                'coherence': float(self.coherence_evaluator.evaluate_strings(prediction=response,input=prompt)['score'])
            }
            return metrics
            
        except Exception as e:
            print(f"评估过程出现错误: {str(e)}")
            return {
                'criteria': 0.0,
                'qa_relevance': 0.0,
                'helpfulness': 0.0,
                'correctness': 0.0,
                'relevance': 0.0,
                'coherence': 0.0
            }
        

    def _save_detailed_metrics(self, evaluation, metrics):
        for name, value in metrics.items():
            EvaluationMetric.objects.create(
                evaluation=evaluation,
                metric_name=name,
                metric_value=value
            )