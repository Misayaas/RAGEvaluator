from rest_framework import serializers
from .models.evaluation import PromptEvaluation, EvaluationMetric
from .models.template import PromptTemplate
from .models.custom_metric import CustomMetric

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

class PromptEvaluationSerializer(serializers.ModelSerializer):
    detailed_metrics = EvaluationMetricSerializer(many=True, read_only=True)
    custom_metrics = serializers.SerializerMethodField()
    
    class Meta:
        model = PromptEvaluation
        fields = '__all__'

    def get_custom_metrics(self, obj):
        return obj.get_custom_metric_scores()