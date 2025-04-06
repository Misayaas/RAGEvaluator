from rest_framework import serializers
from .models.evaluation import PromptEvaluation, EvaluationMetric
from .models.template import PromptTemplate

class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = '__all__'

class EvaluationMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationMetric
        fields = '__all__'

class PromptEvaluationSerializer(serializers.ModelSerializer):
    detailed_metrics = EvaluationMetricSerializer(many=True, read_only=True)
    
    class Meta:
        model = PromptEvaluation
        fields = '__all__'