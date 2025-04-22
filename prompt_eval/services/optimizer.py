from langchain_openai import ChatOpenAI

from eval_master import settings
from ..models.evaluation import PromptEvaluation
from django.core.exceptions import ValidationError
from langchain_core.prompts import PromptTemplate

class PromptOptimizer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="hunyuan-lite",
            temperature=0.6,
            base_url=settings.OPENAI_API_BASE,
            api_key=settings.OPENAI_API_KEY
        )

        self.optimization_suggestion = PromptTemplate(
            input_variables=["prompt", "metrics"],
            template="""请根据以下评估结果分析Prompt的问题，并提供具体的优化建议：
            
原始Prompt: {prompt}

评估结果:
{metrics}

优化建议要求:
1. 指出每个低分指标的具体问题
2. 提供明确的改进方向
3. 不要直接生成优化后的Prompt

请按以下格式返回结果：
优化建议:
1. [指标名称]: [具体问题描述] -> [改进建议]
2. [指标名称]: [具体问题描述] -> [改进建议]"""
        )
        
        self.optimization_prompt = PromptTemplate(
            input_variables=["prompt", "metrics"],
            template="""请根据以下评估结果优化Prompt，并解释优化内容：
            
原始Prompt: {prompt}

评估结果:
{metrics}

优化要求:
1. 保持Prompt的核心意图
2. 针对低分指标进行改进
3. 确保优化后的Prompt更清晰、更有效
4. 给Prompt对应的引导，告诉模型你期望它做什么或者不做什么
5. 可以提供相应的简单示例
6. 告知模型自己的角色

请按以下格式返回结果：
优化后的Prompt: [优化后的Prompt内容]
优化解释: [优化内容的解释]"""
        )


    """根据评估结果获取优化建议，适用于发现问题后手动优化"""
    def get_optimization_suggestions(self, evaluation_id):
        try:
            evaluation = PromptEvaluation.objects.get(id=evaluation_id)
            
            # 获取所有评估指标
            metrics = evaluation.detailed_metrics.all()
            metrics_str = "\n".join([f"{m.metric_name}: {m.metric_value:.2f}" for m in metrics])
            
            # 使用LLM生成优化建议
            result = self.llm.invoke(self.optimization_suggestion.format(
                prompt=evaluation.prompt_text,
                metrics=metrics_str
            ))
            
            return result.content
            
        except PromptEvaluation.DoesNotExist:
            raise ValidationError(f"未找到ID为{evaluation_id}的评估记录")
        except Exception as e:
            raise ValidationError(f"获取优化建议失败: {str(e)}")


    """自动优化Prompt"""
    def auto_optimize_prompt(self, evaluation_id):
        try:
            evaluation = PromptEvaluation.objects.get(id=evaluation_id)
            
            # 获取所有评估指标
            metrics = evaluation.detailed_metrics.all()
            metrics_str = "\n".join([f"{m.metric_name}: {m.metric_value:.2f}" for m in metrics])
            
            # 使用LLM生成优化后的Prompt
            result = self.llm.invoke(self.optimization_prompt.format(
                prompt=evaluation.prompt_text,
                metrics=metrics_str
            ))
            
            # 解析优化后的prompt
            optimized_prompt = result.content.split("优化后的Prompt: ")[1].split("优化解释: ")[0].strip()
            optimization_explanation = result.content.split("优化解释: ")[1].strip()
            return {
                "optimized_prompt": optimized_prompt,
                "optimization_explanation": optimization_explanation
            }
            
        except PromptEvaluation.DoesNotExist:
            raise ValidationError(f"未找到ID为{evaluation_id}的评估记录")
        except Exception as e:
            raise ValidationError(f"自动优化失败: {str(e)}")