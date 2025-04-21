from ragas.metrics import Metric
from typing import Any, List, Optional

class CustomRagasMetric(Metric):
    def __init__(self, name, description, llm):
        super().__init__()
        self.name = name
        self.description = description
        self.llm = llm
        self.threshold = 0.5

    async def _acompute(
        self,
        question: List[str],
        answer: List[str],
        contexts: Optional[List[List[str]]] = None,
        **kwargs: Any,
    ) -> List[float]:
        scores = []
        for q, a, ctx in zip(question, answer, contexts or [[] for _ in question]):
            context_text = "\n".join(ctx) if ctx else ""
            prompt = f"""请根据以下标准评估回答质量，评分范围为0到1。

评估标准：{self.description}

历史上下文：
{context_text}

问题：{q}
回答：{a}

请只输出一个0到1之间的数字作为评分。"""
            
            response = await self.llm.agenerate(prompt)
            try:
                score = float(response)
                scores.append(score)
            except ValueError:
                scores.append(0.0)
        
        return scores