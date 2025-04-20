from ragas import evaluate
from langchain_core.messages import HumanMessage
from ragas.metrics import faithfulness, context_recall, answer_relevancy, context_precision
from langchain_openai import OpenAIEmbeddings
from datasets import Dataset  

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
        self.llm = llm
        self.custom_llm = LangchainLLMWrapper(llm)

        # 修改 embeddings 模型
        v_embeddings = OpenAIEmbeddings(
            model="hunyuan-embedding",  # 指定正确的模型
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        )

        self.metrics = [
            faithfulness,
            # context_recall,
            # answer_relevancy,
            # context_precision
        ]

        faithfulness.llm = self.custom_llm
        # context_recall.llm = self.custom_llm
        # answer_relevancy.llm = self.custom_llm
        # answer_relevancy.embeddings = v_embeddings
        # context_precision.llm = self.custom_llm


    """创建新的评估任务"""
    def create_task(self, name):
        return PromptTask.objects.create(
            name=name
        )

    """创建新的评估并获取大模型响应"""
    def create_and_evaluate(self, task_id, prompt_text):
        try:
            # 1. 创建评估记录
            task = PromptTask.objects.get(id=task_id)
            previous_evaluations = task.evaluations.order_by('version').all()

            # 构建上下文
            if previous_evaluations.exists():
                context = [eval.prompt_text for eval in previous_evaluations]
            else:
                context = [prompt_text]

            evaluation = PromptEvaluation.objects.create(
                task=task,
                prompt_text=prompt_text,
                context=context,
                model_name=self.llm.model_name,
                status='pending',
                version=task.evaluations.count() + 1
            )

            # 2. 获取大模型响应
            message = HumanMessage(content=prompt_text)
            ai_response = self.llm.invoke([message])
            response = ai_response.content

            # 3. 更新响应并评估
            evaluation.update_response(response)
            return self.evaluate_prompt(evaluation)

        except PromptTask.DoesNotExist:
            raise ValidationError(f"未找到ID为{task_id}的任务")
        except Exception as e:
            raise ValidationError(f"评估过程出错: {str(e)}")


    """获取任务的所有评估记录"""
    def get_task_evaluations(self, task_id):
        try:
            task = PromptTask.objects.get(id=task_id)
            return task.evaluations.order_by('version').all()
        except PromptTask.DoesNotExist:
            raise ValidationError(f"未找到ID为{task_id}的任务")


    """评估一个prompt"""
    def evaluate_prompt(self, evaluation):
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


    """计算各项评估指标"""
    def _calculate_metrics(self, prompt, response, context):
        try:
            # 确保所有输入都是字符串
            prompt = str(prompt) if prompt else ""
            response = str(response) if response else ""

            # 如果 context 是列表，直接使用；否则转换为列表
            if isinstance(context, list):
                contexts = context
            else:
                try:
                    contexts = eval(context) if context else [""]
                except:
                    contexts = [context] if context else [""]
            
            # 构建数据集
            data = {
                "question": [prompt],
                "answer": [response],
                "contexts": [contexts]
            }

            dataset = Dataset.from_dict(data)
            # 使用 Ragas 评估
            scores = evaluate(
                dataset=dataset,
                metrics=self.metrics
            )
            
            return {
                'faithfulness': float(scores['faithfulness'][0] if isinstance(scores['faithfulness'], list) else scores['faithfulness']),
                # 'context_recall': float(scores['context_recall']),
                # 'answer_relevancy': float(scores['answer_relevancy'][0] if isinstance(scores['answer_relevancy'], list) else scores['answer_relevancy'])
                # 'context_precision': float(scores['context_precision'])
            }
            
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

    """删除评估任务"""
    def  delete_task(self, task_id):
        try:
            task = PromptTask.objects.get(id=task_id)
            task.delete()
            return True
        except PromptTask.DoesNotExist:
            raise ValidationError(f"未找到ID为{task_id}的任务")