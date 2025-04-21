from rest_framework import serializers
from .models.evaluation import PromptEvaluation, EvaluationMetric
from .models.template import PromptTemplate
from .models.custom_metric import CustomMetric, MetricScore


class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = '__all__'

class EvaluationMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationMetric
        fields = '__all__'

class CustomMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomMetric
        fields = ['id', 'name', 'description', 'created_at']


class MetricScoreSerializer(serializers.ModelSerializer):
    metric_name = serializers.CharField(source='metric.name', read_only=True)

    class Meta:
        model = MetricScore
        fields = ['metric_name', 'score', 'created_at']

class PromptEvaluationSerializer(serializers.ModelSerializer):
    detailed_metrics = EvaluationMetricSerializer(many=True, read_only=True)
    metric_scores = MetricScoreSerializer(many=True, read_only=True)
    
    class Meta:
        model = PromptEvaluation
        fields = [
            'id', 'task', 'prompt_text', 'response', 'context',
            'model_name', 'status', 'version', 'created_at',
            'faithfulness_score', 'relevance_score',
            'coherence_score', 'helpfulness_score',
            'detailed_metrics' ,
            'metric_scores'
        ]
        custom_metrics = serializers.SerializerMethodField()

    def get_custom_metrics(self, obj):
        return obj.get_custom_metric_scores()