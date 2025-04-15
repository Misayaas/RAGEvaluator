from rest_framework import viewsets, status
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
    def create_evaluation(self, request):
        """创建新的评估任务"""
        evaluator = PromptEvaluator()
        evaluation = evaluator.create_evaluation(
            prompt_text=request.data.get('prompt_text'),
            context=request.data.get('context'),
            model_name=request.data.get('model_name', 'default')
        )
        return Response(self.get_serializer(evaluation).data)

    @action(detail=True, methods=['post'])
    def update_response(self, request, pk=None):
        """更新模型响应并评估"""
        evaluator = PromptEvaluator()
        evaluation = evaluator.update_response(
            evaluation_id=pk,
            response_text=request.data.get('response_text')
        )
        return Response(self.get_serializer(evaluation).data)

    @action(detail=True, methods=['post'])
    def create_next_version(self, request, pk=None):
        """创建新版本的评估"""
        evaluator = PromptEvaluator()
        new_evaluation = evaluator.create_next_version(
            evaluation_id=pk,
            new_prompt_text=request.data.get('new_prompt_text')
        )
        return Response(self.get_serializer(new_evaluation).data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """获取评估历史"""
        evaluator = PromptEvaluator()
        history = evaluator.get_evaluation_history(evaluation_id=pk)
        return Response(self.get_serializer(history, many=True).data)

    