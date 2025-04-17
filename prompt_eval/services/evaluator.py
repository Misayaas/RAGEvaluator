from ragas import evaluate
from ragas.metrics import faithfulness, context_recall, answer_relevancy, context_precision
from langchain_openai import OpenAIEmbeddings
from datasets import Dataset  # 添加这个导入

from eval_master import settings
from ..models.evaluation import PromptEvaluation, EvaluationMetric
from ..models.task import PromptTask
from django.core.exceptions import ValidationError
from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper

class PromptEvaluator:
    """初始化"""
    def __init__(self):
        llm = ChatOpenAI(
            model="hunyuan-lite",
            temperature=0,
            base_url=settings.OPENAI_API_BASE,
            api_key=settings.OPENAI_API_KEY
        )
        self.custom_llm = LangchainLLMWrapper(llm)

        # 修改 embeddings 模型
        v_embeddings = OpenAIEmbeddings(
            model="hunyuan-embedding",  # 指定正确的模型
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )

        self.metrics = [
            # faithfulness,
            # context_recall,
            answer_relevancy,
            # context_precision
        ]

        # faithfulness.llm = self.custom_llm
        # context_recall.llm = self.custom_llm
        answer_relevancy.llm = self.custom_llm
        answer_relevancy.embeddings = v_embeddings
        # context_precision.llm = self.custom_llm


    """创建新的评估任务"""
    def create_task(self, name, description=None, goal=None):
        return PromptTask.objects.create(
            name=name,
            description=description,
            goal=goal,
            status='active'
        )

    """为指定任务创建新的评估"""
    def create_evaluation_for_task(self, task_id, prompt_text, context=None, model_name="default"):
        try:
            task = PromptTask.objects.get(id=task_id)

            # 获取最新的评估记录
            latest_evaluation = task.evaluations.order_by('-version').first()

            return PromptEvaluation.objects.create(
                task=task,
                prompt_text=prompt_text,
                context=context or (latest_evaluation.context if latest_evaluation else None),
                model_name=model_name,
                status='pending',
                version=task.evaluations.count() + 1
            )
        except PromptTask.DoesNotExist:
            raise ValidationError(f"未找到ID为{task_id}的任务")

    """使用大模型进行评估并返回响应"""
    def evaluate_with_llm(self, evaluation_id):
        try:
            evaluation = PromptEvaluation.objects.get(id=evaluation_id)
            
            # 调用大模型获取响应
            # TODO: 这里需要实现调用大模型的逻辑


            # 更新响应并进行评估
            response = "这是一个示例响应"
            evaluation.update_response(response)
            return self.evaluate_prompt(evaluation)
            
        except PromptEvaluation.DoesNotExist:
            raise ValidationError(f"未找到ID为{evaluation_id}的评估记录")
        except Exception as e:
            raise ValidationError(f"评估过程出错: {str(e)}")


    """获取任务的所有评估记录"""
    def get_task_evaluations(self, task_id):
        try:
            task = PromptTask.objects.get(id=task_id)
            return task.evaluations.order_by('version').all()
        except PromptTask.DoesNotExist:
            raise ValidationError(f"未找到ID为{task_id}的任务")


    """更新模型响应并开始评估"""
    def update_response(self, evaluation_id, response_text):
        try:
            evaluation = PromptEvaluation.objects.get(id=evaluation_id)
            evaluation.update_response(response_text)
            return self.evaluate_prompt(evaluation)
        except PromptEvaluation.DoesNotExist:
            raise ValidationError(f"未找到ID为{evaluation_id}的评估记录")


    """评估一个prompt"""
    def evaluate_prompt(self, evaluation):
        if evaluation.status != 'responded':
            raise ValidationError("只能评估已有响应的记录")

        try:
            evaluation.status = 'evaluating'
            evaluation.save()
            
            print("prompt: " + evaluation.prompt_text)
            print("response: " + evaluation.response)

            # 计算评估指标
            metrics = self._calculate_metrics(
                evaluation.prompt_text,
                evaluation.response,
                evaluation.context
            )
            
            # 更新评估记录
            # evaluation.faithfulness_score = metrics.get('faithfulness', 0.0)
            # evaluation.context_recall_score = metrics.get('context_recall', 0.0)
            evaluation.answer_relevancy_score = metrics.get('answer_relevancy', 0.0)
            # evaluation.context_precision_score = metrics.get('context_precision', 0.0)
            evaluation.status = 'completed'
            evaluation.save()
            
            # 保存详细指标
            self._save_detailed_metrics(evaluation, metrics)
            return evaluation
            
        except Exception as e:
            evaluation.status = 'failed'
            evaluation.save()
            raise ValidationError(f"评估过程出现错误: {str(e)}")


    """计算各项评估指标"""
    def _calculate_metrics(self, prompt, response, context):
        try:
            # 确保所有输入都是字符串
            prompt = str(prompt) if prompt else ""
            response = str(response) if response else ""
            context = str(context) if context else ""
            
            # 构建数据集
            data = {
                "question": [prompt],
                "answer": [response],
                "context": [[context]] if context else [[""]]
            }

            try:
                dataset = Dataset.from_dict(data)
                # 使用 Ragas 评估
                scores = evaluate(
                    dataset=dataset,
                    metrics=self.metrics
                )
                
                return {
                    # 'faithfulness': float(scores['faithfulness']),
                    # 'context_recall': float(scores['context_recall']),
                    'answer_relevancy': float(scores['answer_relevancy'][0] if isinstance(scores['answer_relevancy'], list) else scores['answer_relevancy'])
                    # 'context_precision': float(scores['context_precision'])
                }

            except Exception as inner_e:
                print("评估过程错误:", str(inner_e))
                return {'answer_relevancy': 0.5}  # 返回一个默认值
            
        except Exception as e:
            print("数据处理错误:", str(e))
            raise ValidationError(f"指标计算错误: {str(e)}")

    def _save_detailed_metrics(self, evaluation, metrics):
        """保存详细评估指标"""
        for name, value in metrics.items():
            EvaluationMetric.objects.create(
                evaluation=evaluation,
                metric_name=name,
                metric_value=value
            )