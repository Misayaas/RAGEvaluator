from ..models.evaluation import PromptEvaluation, EvaluationMetric
from ..models.template import PromptTemplate
from ragas import evaluate
from datasets import Dataset
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

    # 评估指标计算逻辑
    def _calculate_metrics(self, prompt, response, context):
        # 构建评估数据集
        eval_dataset = Dataset.from_dict({
            "question": [prompt],
            "answer": [response],
            "contexts": [[context]],
            # 标准答案难以确定，暂时只使用不需要ground_truths的指标
            # "ground_truths": [[""]] 
        })
        
        # 使用ragas进行评估
        try:
            # 执行评估并获取结果
            result = evaluate(
                eval_dataset,
                metrics=[
                    "faithfulness",     # 答案是否忠实于上下文
                    "context_relevancy",  # 上下文相关性
                    "answer_relevancy"    # 答案与问题的相关性
                ]
            )
            
            # 提取评估指标
            metrics = {
                'relevance': float(result['answer_relevancy']),
                'coherence': float(result['faithfulness']),
                'context_relevance': float(result['context_relevancy'])
            }
            
            return metrics
        except Exception as e:
            print(f"评估过程中发生错误: {e}")
            return {}
        

    def _save_detailed_metrics(self, evaluation, metrics):
        for name, value in metrics.items():
            EvaluationMetric.objects.create(
                evaluation=evaluation,
                metric_name=name,
                metric_value=value
            )