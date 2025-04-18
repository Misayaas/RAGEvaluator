## 实现RAG系统的评估逻辑(包括检索和生成两部分)
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_openai import OpenAIEmbeddings
from datasets import Dataset

from eval_master import settings
from rag_eval.models.evaluation import EvaluationResult, RAGEvaluation
from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper
import csv
import numpy as np
import time
import math

def read_csv_file(csv_file):

    # 使用 utf-8 编码方式打开 CSV 文件
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        questions = []
        ground_truths = []
        answers = []
        contexts = []
        reference = []

        for row in csv_reader:
            questions.append(row.get('question', '')) 
            ground_truths.append([row.get('ground_truth', '')]) 
            answers.append(row.get('answer', '')) 
            contexts.append([row.get('contexts', '')]) 
            reference.append(row.get('reference', '')) 
            
        return {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truths": ground_truths,
            "reference": reference
        }

def filterNAN(v: list):
    return list(filter(lambda x: not isinstance(x, float) or not math.isnan(x), v))

def evaluate_rag(file_path : str) :
    llm = ChatOpenAI(
            model="hunyuan-lite",
            temperature=0,
            base_url=settings.OPENAI_API_BASE,
            api_key=settings.OPENAI_API_KEY
        )

    custom_llm = LangchainLLMWrapper(llm)

    v_embeddings = OpenAIEmbeddings(
        model="hunyuan-embedding",  # 指定正确的模型
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_API_BASE
    )

    answer_relevancy.llm = custom_llm
    answer_relevancy.embeddings = v_embeddings

    faithfulness.llm = custom_llm
    context_recall.llm = custom_llm
    context_precision.llm = custom_llm

    data = read_csv_file(file_path)
    dataset = Dataset.from_dict(data)
    result = evaluate(
    dataset = dataset, 
    metrics=[
        context_precision,
        context_recall,
        faithfulness,
        # answer_relevancy,
    ],
    )

    return {"faithfulness_score": np.mean(filterNAN(result['faithfulness']))}
