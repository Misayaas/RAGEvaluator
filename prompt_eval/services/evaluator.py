from langchain_core.prompts import PromptTemplate
from ragas import evaluate
from langchain_core.messages import HumanMessage
from ragas.metrics import faithfulness, AspectCritic
from datasets import Dataset  
from langchain.evaluation import load_evaluator, EvaluatorType
from langchain.evaluation.criteria import Criteria

from eval_master import settings
from ..models.evaluation import AspectMetric, PromptEvaluation, EvaluationMetric
from ..models.task import PromptTask
from django.core.exceptions import ValidationError
from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper

import re

class PromptEvaluator:
    """初始化"""
    def __init__(self):
        llm = ChatOpenAI(
            model="hunyuan-lite",
            temperature=0.8,
            base_url=settings.OPENAI_API_BASE,
            api_key=settings.OPENAI_API_KEY
        )
        self.llm = llm
        self.custom_llm = LangchainLLMWrapper(llm)

        self.metrics = [
            faithfulness
        ]

        faithfulness.llm = self.custom_llm

        # 自定义评估提示词
        evaluation_prompts = {
            "relevance": PromptTemplate(
                input_variables=["input", "output", "criteria"],
                template="""请评估回答与问题的相关性，评分范围为0到1。

评估标准：{criteria}

评分细则：
1.0: 完全相关，准确回答问题的所有方面
0.8: 大部分相关，回答了问题的主要方面
0.6: 基本相关，但有一些不够准确或遗漏
0.4: 部分相关，但存在明显偏差
0.2: 略微相关，但大部分内容偏离主题
0.0: 完全不相关

输入问题：{input}
模型回答：{output}

"""),

            "coherence": PromptTemplate(
                input_variables=["input", "output", "criteria"],
                template="""请评估回答的连贯性，评分范围为0到1。

评估标准：{criteria}

评分细则：
1.0: 结构完整，逻辑严密，表达清晰流畅
0.8: 整体连贯，偶有小瑕疵
0.6: 基本连贯，但有些跳跃
0.4: 部分内容混乱，逻辑不够清晰
0.2: 大部分内容缺乏连贯性
0.0: 完全混乱，难以理解

输入问题：{input}
模型回答：{output}

请只输出一个0到1之间的数字作为评分，也就是score，不要包含任何其他文字。"""),

            "helpfulness": PromptTemplate(
                input_variables=["input", "output", "criteria"],
                template="""请评估回答的帮助程度，评分范围为0到1。

评估标准：{criteria}

评分细则：
1.0: 提供了完整、实用的解决方案
0.8: 提供了有价值的信息和具体建议
0.6: 提供了一般性的帮助
0.4: 提供了有限的帮助
0.2: 帮助很少，难以应用
0.0: 完全没有帮助价值

输入问题：{input}
模型回答：{output}

请只输出一个0到1之间的数字作为评分，也就是score，不要包含任何其他文字。"""),
        }

        # 使用自定义提示词初始化评估器
        self.lc_evaluators = {}
        for name, prompt in evaluation_prompts.items():
            self.lc_evaluators[name] = load_evaluator(
                EvaluatorType.CRITERIA,
                criteria=getattr(Criteria, name.upper()),
                llm=llm,
                prompt=prompt
            )

        # # 添加 LangChain 评估器
        # self.lc_evaluators = {
        #     "relevance": load_evaluator(EvaluatorType.CRITERIA, criteria=Criteria.RELEVANCE, llm=llm),
        #     "coherence": load_evaluator(EvaluatorType.CRITERIA, criteria=Criteria.COHERENCE, llm=llm),
        #     "helpfulness": load_evaluator(EvaluatorType.CRITERIA, criteria=Criteria.HELPFULNESS, llm=llm)
        # }

    """创建新的评估任务"""
    def create_task(self, name):
        return PromptTask.objects.create(
            name=name
        )


    """获取所有评估任务"""
    def get_all_tasks(self):
        return PromptTask.objects.all()


    """创建任务的自定义评估指标"""
    def create_aspect_metric(self, task_id, name, description):
        try:
            task = PromptTask.objects.get(id=task_id)
            metric = AspectMetric.objects.create(
                task=task,
                name=name,
                description=description
            )
            return metric
        except PromptTask.DoesNotExist:
            raise ValidationError(f"未找到ID为{task_id}的任务")
        except Exception as e:
            raise ValidationError(f"创建自定义指标失败: {str(e)}")


    """获取任务的所有自定义评估指标"""
    def get_task_aspect_metrics(self, task_id):
        try:
            task = PromptTask.objects.get(id=task_id)
            return task.aspect_metrics.all()
        except PromptTask.DoesNotExist:
            raise ValidationError(f"未找到ID为{task_id}的任务")


    """删除任务的自定义评估指标"""
    def delete_aspect_metric(self, metric_id):
        try:
            metric = AspectMetric.objects.get(id=metric_id)
            metric.delete()
            return True
        except AspectMetric.DoesNotExist:
            raise ValidationError(f"未找到ID为{metric_id}的指标")


    """创建新的评估并获取大模型响应"""
    def create_and_evaluate(self, task_id, prompt_text, selected_metrics=None):
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
            return self.evaluate_prompt(evaluation, selected_metrics)

        except PromptTask.DoesNotExist:
            raise ValidationError(f"未找到ID为{task_id}的任务")
        except Exception as e:
            raise ValidationError(f"评估过程出错: {str(e)}")


    """评估给定的评估记录"""
    def evaluate_prompt(self, evaluation, selected_metrics=None):
        if evaluation.status != 'responded':
            raise ValidationError("只能评估已有响应的记录")
    
        try:
            evaluation.status = 'evaluating'
            evaluation.save()
    
            # 重置metrics列表，避免重复添加
            self.metrics = [faithfulness]  # 保留基础指标
    
            # 加载选中的自定义指标
            if selected_metrics:
                task_metrics = AspectMetric.objects.filter(
                    task=evaluation.task,
                    id__in=selected_metrics
                )
                
                # 添加 AspectCritic 指标
                for metric in task_metrics:
                    aspect_critic = AspectCritic(
                        name=metric.name,
                        definition=metric.description,
                        llm=self.custom_llm
                    )
                    self.metrics.append(aspect_critic)

            # 计算 Ragas 评估指标
            ragas_metrics = self._calculate_ragas_metrics(
                evaluation.prompt_text,
                evaluation.response,
                evaluation.context
            )

            # 计算 LangChain 评估指标
            lc_metrics = self._calculate_langchain_metrics(
                evaluation.prompt_text,
                evaluation.response
            )

            # 合并所有指标
            metrics = {**ragas_metrics, **lc_metrics}
            
            # 更新评估记录
            evaluation.faithfulness_score = metrics.get('faithfulness', 0.0)
            evaluation.relevance_score = metrics.get('relevance', 0.0)
            evaluation.coherence_score = metrics.get('coherence', 0.0)
            evaluation.helpfulness_score = metrics.get('helpfulness', 0.0)
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
    def _calculate_ragas_metrics(self, prompt, response, context):
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

            contexts = [str(ctx) if ctx else "" for ctx in contexts]
            
            
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
            
            metrics_result = {}
            for metric in self.metrics:
                metric_name = metric.name
                try:
                    score = scores[metric_name][0]
                    metrics_result[metric_name] = float(score)
                except Exception as e:
                    print(f"处理指标 {metric_name} 时出错: {str(e)}")
                    metrics_result[metric_name] = 0.0

            return metrics_result
            
        except Exception as e:
            print("数据处理错误:", str(e))
            raise ValidationError(f"指标计算错误: {str(e)}")

    def _calculate_langchain_metrics(self, prompt, response):
        try:
            metrics = {}
            for name, evaluator in self.lc_evaluators.items():
                result = evaluator.evaluate_strings(
                    prediction=response,
                    input=prompt
                )
                if isinstance(result, dict):
                    if result.get('score') is not None:
                        if isinstance(result['score'], str):
                            match = re.search(r'\d+\.?\d*', result['score'])
                            score = float(match.group()) if match else 0.0
                        else:
                            score = result['score']
                        score = result['score']
                    elif result.get('value') is not None:
                        if isinstance(result['value'], str):
                            match = re.search(r'\d+\.?\d*', result['value'])
                            score = float(match.group()) if match else 0.0
                        else:
                            score = result['value']
                    elif result.get('reasoning') is not None:
                        if isinstance(result['reasoning'], str):
                            match = re.search(r'\d+\.?\d*', result['reasoning'])
                            score = float(match.group()) if match else 0.0
                        else:
                            score = result['reasoning']
                    else:
                        score = 0.0
                else:
                    if isinstance(result, str):
                        match = re.search(r'\d+\.?\d*', result)
                        score = float(match.group()) if match else 0.0
                    else:
                        score = result

                metrics[name] = float(score) if score is not None else 0.0
            return metrics
        except Exception as e:
            print(f"LangChain 评估错误: {str(e)}")
            return {}

    def _save_detailed_metrics(self, evaluation, metrics):
        """保存详细评估指标"""
        for name, value in metrics.items():
            metric_details = None
            if name not in ['faithfulness', 'relevance', 'coherence', 'helpfulness']:
                try:
                    aspect_metric = AspectMetric.objects.get(name=name, task=evaluation.task)
                    metric_details = aspect_metric.description
                except AspectMetric.DoesNotExist:
                    pass
            else:
                metric_details = "默认指标: " + name

            EvaluationMetric.objects.create(
                evaluation=evaluation,
                metric_name=name,
                metric_value=value,
                metric_details=metric_details
            )


    """保存指标评分"""
    def save_aspect_critic(self, evaluation: PromptEvaluation, scores):
        for metric_name, score in scores.items():
            try:
                EvaluationMetric.objects.update_or_create(
                    evaluation=evaluation,
                    metric_name=metric_name,
                    defaults={'metric_value': score}
                )
            except Exception as e:
                print(f"保存指标 {metric_name} 评分失败: {str(e)}")


    """获取任务的所有评估记录"""
    def get_task_evaluations(self, task_id):
        try:
            task = PromptTask.objects.get(id=task_id)
            return task.evaluations.all().order_by('-created_at')
        except PromptTask.DoesNotExist:
            raise ValidationError(f"未找到ID为{task_id}的任务")
        except Exception as e:
            raise ValidationError(f"获取评估记录失败: {str(e)}")

    """删除评估任务"""
    def delete_task(self, task_id):
        try:
            task = PromptTask.objects.get(id=task_id)

            for evaluation in task.evaluations.all():
                evaluation.detailed_metrics.all().delete()
                evaluation.delete()

            task.aspect_metrics.all().delete()

            task.delete()
            return True
        except PromptTask.DoesNotExist:
            raise ValidationError(f"未找到ID为{task_id}的任务")


    """删除指定评估记录"""
    def delete_evaluation(self, evaluation_id):
        try:
            evaluation = PromptEvaluation.objects.get(id=evaluation_id)
            evaluation.detailed_metrics.all().delete()
            evaluation.delete()
            return True
        except PromptEvaluation.DoesNotExist:
            raise ValidationError(f"未找到ID为{evaluation_id}的评估记录")
