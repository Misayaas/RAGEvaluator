from rest_framework import serializers
from .models.evaluation import RAGEvaluation, EvaluationResult
from .models.task import RAGTask

class EvaluationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationResult
        fields = ['id', 'evaluation', 'metric_name', 'metric_value', 'metric_details']
        read_only_fields = ['id', 'evaluation']


class RAGEvaluationSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=RAGTask.objects.all())
    detailed_metrics = EvaluationResultSerializer(many=True, read_only=True)

    class Meta:
        model = RAGEvaluation
        fields = ['id', 'task', 'name', 'evaluated_file',
                  'faithfulness_score', 'answer_relevancy_score', 'context_relevancy_score',
                  'context_precision_score', 'context_recall_score', 'response_time',
                  'created_at', 'detailed_metrics']
        read_only_fields = ['id', 'task', 'evaluated_file', 'faithfulness_score', 'answer_relevancy_score',
                            'context_relevancy_score', 'context_precision_score',
                            'context_recall_score', 'response_time', 'created_at', 'detailed_metrics']


class RAGTaskSerializer(serializers.ModelSerializer):
    evaluations = RAGEvaluationSerializer(many=True, read_only=True)

    class Meta:
        model = RAGTask
        fields = ['id', 'name', 'description', 'evaluations']
        read_only_fields = ['id', 'evaluations']
