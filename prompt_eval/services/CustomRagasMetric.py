from typing import Any, Dict, List, Sequence, Type, Set, Optional
from ragas.metrics.base import MetricWithLLM, SingleTurnMetric, MetricType
from ragas.dataset_schema import SingleTurnSample
from dataclasses import dataclass, field
from ragas.callbacks import Callbacks

@dataclass
class CustomRagasMetric(MetricWithLLM, SingleTurnMetric):
    """自定义评估指标类"""
    
    # 先定义父类中的必需参数
    llm: Any  # LLM 实例
    # 再定义自定义参数
    name: str = "custom_metric"  # 指标名称，设置默认值
    description: str = ""  # 评估标准描述，设置默认值
    
    # 定义必需的列
    _required_columns: Dict[MetricType, Set[str]] = field(
        default_factory=lambda: {
            MetricType.SINGLE_TURN: {"question", "answer"}
        }
    )
    
    async def _single_turn_ascore(self, sample: SingleTurnSample, callbacks: Callbacks) -> float:
        """异步评分方法"""
        try:
            # 构建评估提示词
            prompt = f"""请根据以下标准评估回答的质量，评分范围为0到1：

评估标准：{self.description}

问题：{sample.question}
回答：{sample.answer}

请只输出一个0到1之间的数字作为评分，不要包含任何其他文字。"""

            # 获取评分
            result = await self.llm.agenerate(prompt)
            result_text = result.content
            
            try:
                # 尝试将结果转换为浮点数
                score = float(result_text.strip())
                # 确保分数在0-1之间
                return max(0.0, min(1.0, score))
            except (ValueError, TypeError):
                print(f"无法解析评分结果: '{result_text}'")
                return 0.5  # 默认中等分数
        except Exception as e:
            print(f"评分过程出错: {str(e)}")
            return 0.5