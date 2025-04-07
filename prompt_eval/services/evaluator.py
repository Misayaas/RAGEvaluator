from ragas.metrics import faithfulness
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
        evaluation.faithfulness_score = metrics['faithfulness']
        evaluation.answer_relevancy_score = metrics['answer_relevancy']
        evaluation.context_relevancy_score = metrics['context_relevancy']
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
                    faithfulness(),
                    answer_relevancy(),
                    context_relevancy()
                ]
            )
            
            # 提取评估指标
            metrics = {
                'faithfulness': float(result['faithfulness']),
                'answer_relevancy': float(result['answer_relevancy']),
                'context_relevancy': float(result['context_relevancy'])
            }
            
            return metrics
        except Exception as e:
            print(f"评估过程出现错误: {str(e)}")
            return {
                'faithfulness': 0.0,
                'answer_relevancy': 0.0,
                'context_relevancy': 0.0
            }
        

    def _save_detailed_metrics(self, evaluation, metrics):
        for name, value in metrics.items():
            EvaluationMetric.objects.create(
                evaluation=evaluation,
                metric_name=name,
                metric_value=value
            )