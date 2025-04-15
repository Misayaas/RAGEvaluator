from rest_framework import serializers
from .models.evaluation import RAGEvaluation, EvaluationResult

class EvaluationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationResult
        fields = ['id', 'evaluation', 'metric_name', 'metric_value', 'metric_details']
        read_only_fields = ['id']

class RAGEvaluationSerializer(serializers.ModelSerializer):
    detailed_metrics = EvaluationResultSerializer(many=True, read_only=True)

    class Meta:
        model = RAGEvaluation
        fields = ['id', 'name', 'description', 'query', 'retrieved_docs', 'generated_answer',
                  'faithfulness_score', 'answer_relevancy_score', 'context_relevancy_score',
                  'context_precision_score', 'context_recall_score', 'response_time',
                  'created_at', 'batch_id', 'detailed_metrics']
        read_only_fields = ['id', 'faithfulness_score', 'answer_relevancy_score',
                            'context_relevancy_score', 'context_precision_score',
                            'context_recall_score', 'response_time', 'created_at', 'detailed_metrics']
