from rest_framework import serializers
from .models.evaluation import PromptEvaluation, EvaluationMetric
from .models.task import PromptTask
from .models.template import PromptTemplate
from .models.evaluation import AspectMetric

class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = '__all__'

class PromptTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTask
        fields = ['id', 'name', 'created_at', 'updated_at']

class EvaluationMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationMetric
        fields = '__all__'

class AspectMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = AspectMetric
        fields = ['id', 'name', 'description', 'created_at']

class PromptEvaluationSerializer(serializers.ModelSerializer):
    detailed_metrics = EvaluationMetricSerializer(many=True, read_only=True)
    
    class Meta:
        model = PromptEvaluation
        fields = [
            'id', 'task', 'prompt_text', 'response', 'context',
            'model_name', 'status', 'version', 'created_at',
            'faithfulness_score', 'relevance_score',
            'coherence_score', 'helpfulness_score',
            'detailed_metrics'
        ]

class MetricTestResultSerializer(serializers.Serializer):
    metric_id = serializers.IntegerField()
    metric_name = serializers.CharField()
    score = serializers.FloatField()
    test_prompt = serializers.CharField()
    test_response = serializers.CharField()

class OptimizedPromptSerializer(serializers.Serializer):
    optimized_prompt = serializers.CharField()
    optimization_explanation = serializers.CharField()