## 实现RAG系统的评估逻辑(包括检索和生成两部分)
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset
from rag_eval.models.evaluation import EvaluationResult, RAGEvaluation
import uuid
import time

class RAGEvaluator:
    def __init__(self):
        self.batch_id = str(uuid.uuid4())

    def evaluate_retrieval(self, query, retrieved_docs):
        # 构建评估数据集
        eval_dataset = Dataset.from_dict({
            "question": [query],
            "contexts": [retrieved_docs],
            "answer": [""],  # ragas需要answer字段，但检索评估不需要实际值
        })

        try:
            result = evaluate(
                eval_dataset,
                metrics=[
                    context_precision(),  # 检索的精确度
                    context_recall(),     # 检索的召回率
                ]
            )
            
            # 将评估结果转换为浮点数
            metrics = {
                'context_precision': float(result['context_precision'][0]),
                'context_recall': float(result['context_recall'][0]),
            }
            return metrics
            
        except Exception as e:
            print(f"检索评估出现错误: {str(e)}")
            return {
                'context_precision': 0.0,
                'context_recall': 0.0,
            }

    def evaluate_generation(self, question, answer, contexts):
        # 构建评估数据集
        eval_dataset = Dataset.from_dict({
            "question": [question],
            "answer": [answer],
            "contexts": [contexts]
        })

        try:
            result = evaluate(
                eval_dataset,
                metrics=[
                    faithfulness(),     # 答案忠实度
                    answer_relevancy(), # 答案相关性
                ]
            )
            
            metrics = {
                'faithfulness': float(result['faithfulness'][0]),
                'answer_relevancy': float(result['answer_relevancy'][0]),
            }
            return metrics
            
        except Exception as e:
            print(f"评估过程出现错误: {str(e)}")
            return {
                'faithfulness': 0.0,
                'answer_relevancy': 0.0,
            }
        
    # 综合评估RAG应用性能
    def evaluate_overall(self, query, retrieved_docs, generated_answer):
        start_time = time.time()

        # 获取评估指标
        retrieval_metrics = self.evaluate_retrieval(query, retrieved_docs)
        generation_metrics = self.evaluate_generation(query, generated_answer, retrieved_docs)
        
        # 合并评估结果
        overall_metrics = {
            **retrieval_metrics,
            **generation_metrics,
            'overall_score': self._calculate_overall_score(retrieval_metrics, generation_metrics)
        }

        # 创建评估记录
        evaluation = RAGEvaluation.objects.create(
            name=f"RAG评估-{time.strftime('%Y%m%d%H%M%S')}",  # 使用时间戳作为默认名称
            description=f"查询: {query[:50]}...",  # 使用查询内容作为默认描述
            query=query,
            retrieved_docs=retrieved_docs,
            generated_answer=generated_answer,
            # evaluated_file=evaluated_file or "",
            batch_id=self.batch_id,
            # 检索评估指标
            context_precision_score=retrieval_metrics['context_precision'],
            context_recall_score=retrieval_metrics['context_recall'],
            faithfulness_score=generation_metrics['faithfulness'],
            answer_relevancy_score=generation_metrics['answer_relevancy'],
            overall_score=overall_metrics['overall_score'],
            # 性能指标
            response_time=(time.time() - start_time) * 1000,  # 毫秒
        )

        self._save_detailed_metrics(evaluation, overall_metrics)

        return evaluation

    # 计算综合得分(权重可以调整)
    def _calculate_overall_score(self, retrieval_metrics, generation_metrics, rate=[0.5, 0.5]):
        weights = {
            'retrieval': rate[0],
            'generation': rate[1]
        }
        
        retrieval_score = sum(retrieval_metrics.values()) / len(retrieval_metrics)
        generation_score = sum(generation_metrics.values()) / len(generation_metrics)
        
        overall_score = (
            weights['retrieval'] * retrieval_score +
            weights['generation'] * generation_score
        )
        
        return overall_score

    def _save_detailed_metrics(self, evaluation, metrics):
            for name, value in metrics.items():
                EvaluationResult.objects.create(
                    evaluation=evaluation,
                    metric_name=name,
                    metric_value=value
                )
