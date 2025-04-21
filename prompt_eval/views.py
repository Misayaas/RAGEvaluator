from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models.evaluation import PromptEvaluation
from .serializers import PromptEvaluationSerializer
from .services.evaluator import PromptEvaluator
from django.core.exceptions import ValidationError

from .serializers import (
    PromptEvaluationSerializer, 
    CustomMetricSerializer,
    EvaluationMetricSerializer
)

class PromptEvaluationViewSet(viewsets.ModelViewSet):
    queryset = PromptEvaluation.objects.all()
    serializer_class = PromptEvaluationSerializer
    
    @action(detail=False, methods=['post'])
    def create_task(self, request):
        """创建新的评估任务"""
        evaluator = PromptEvaluator()
        task = evaluator.create_task(
            name=request.data.get('name'),
        )
        return Response({'task_id': task.id})

    @action(detail=False, methods=['post'])
    def create_and_evaluate(self, request):
        """创建新的评估并执行评估"""
        evaluator = PromptEvaluator()
        evaluation = evaluator.create_and_evaluate(
            task_id=request.data.get('task_id'),
            prompt_text=request.data.get('prompt_text'),
            selected_metrics=request.data.get('selected_metrics', [])  # 添加选中的指标ID列表
        )
        return Response(self.get_serializer(evaluation).data)

    @action(detail=True, methods=['get'])
    def task_evaluations(self, request, pk=None):
        """获取任务的所有评估记录"""
        evaluator = PromptEvaluator()
        evaluations = evaluator.get_task_evaluations(task_id=pk)
        return Response(self.get_serializer(evaluations, many=True).data)

    @action(detail=True, methods=['delete'])
    def delete_task(self, request, pk=None):
        """删除评估任务"""
        evaluator = PromptEvaluator()
        evaluator.delete_task(task_id=pk)
        return Response({'message': '任务删除成功'})

    @action(detail=True, methods=['post'])
    def create_custom_metric(self, request, pk=None):
        """创建自定义指标"""
        try:
            name = request.data.get('name')
            description = request.data.get('description')
            
            evaluator = PromptEvaluator()
            metric = evaluator.create_custom_metric(pk, name, description)
            
            serializer = CustomMetricSerializer(metric)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['get'])
    def custom_metrics(self, request, pk=None):
        """获取任务的所有自定义指标"""
        try:
            evaluator = PromptEvaluator()
            metrics = evaluator.get_task_custom_metrics(pk)
            
            serializer = CustomMetricSerializer(metrics, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['delete'])
    def delete_custom_metric(self, request, pk=None):
        """删除自定义指标"""
        try:
            evaluator = PromptEvaluator()
            evaluator.delete_custom_metric(pk)
            return Response({'message': '删除成功'})
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    