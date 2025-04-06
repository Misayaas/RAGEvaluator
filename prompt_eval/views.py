from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models.template import PromptTemplate
from .models.evaluation import PromptEvaluation
from .serializers import PromptTemplateSerializer, PromptEvaluationSerializer
from .services.evaluator import PromptEvaluator

class PromptTemplateViewSet(viewsets.ModelViewSet):
    queryset = PromptTemplate.objects.all()
    serializer_class = PromptTemplateSerializer
    
    @action(detail=True, methods=['post'])
    def create_new_version(self, request, pk=None):
        template = self.get_object()
        new_template = template.create_new_version()
        return Response(self.get_serializer(new_template).data)

class PromptEvaluationViewSet(viewsets.ModelViewSet):
    queryset = PromptEvaluation.objects.all()
    serializer_class = PromptEvaluationSerializer
    
    @action(detail=False, methods=['post'])
    def evaluate(self, request):
        evaluator = PromptEvaluator()
        evaluation = evaluator.evaluate_prompt(
            template_id=request.data.get('template_id'),
            prompt_text=request.data.get('prompt_text'),
            response=request.data.get('response'),
            context=request.data.get('context'),
            model_name=request.data.get('model_name')
        )
        return Response(self.get_serializer(evaluation).data)