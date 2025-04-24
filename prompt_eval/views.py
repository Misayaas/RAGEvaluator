from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models.evaluation import PromptEvaluation
from .services.evaluator import PromptEvaluator
from django.core.exceptions import ValidationError

from .serializers import (
    PromptEvaluationSerializer, 
    AspectMetricSerializer,
    EvaluationMetricSerializer
)
from .services.optimizer import PromptOptimizer


class PromptEvaluationViewSet(viewsets.ModelViewSet):
    queryset = PromptEvaluation.objects.all()
    serializer_class = PromptEvaluationSerializer
    
    @action(detail=False, methods=['post'])
    def create_task(self, request):
        """创建新的评估任务"""
        evaluator = PromptEvaluator()
        task = evaluator.create_task(
            name=request.data.get('name')
        )
        return Response({'task_id': task.id})


    @action(detail=False, methods=['get'])
    def list_tasks(self, request):
        """获取所有任务"""
        evaluator = PromptEvaluator()
        tasks = evaluator.get_all_tasks()
        return Response(self.get_serializer(tasks, many=True).data)

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

    @action(detail=False, methods=['get'])
    def task_evaluations(self, request):
        """获取任务的所有评估记录"""
        evaluator = PromptEvaluator()
        evaluations = evaluator.get_task_evaluations(task_id=request.query_params.get('task_id'))
        return Response(self.get_serializer(evaluations, many=True).data)

    @action(detail=False, methods=['delete'])
    def delete_task(self, request):
        """删除评估任务"""
        evaluator = PromptEvaluator()
        evaluator.delete_task(task_id=request.query_params.get('task_id'))
        return Response({'message': '任务删除成功'})

    @action(detail=False, methods=['post'])
    def create_aspect_metric(self, request):
        """创建评估指标"""
        try:
            evaluator = PromptEvaluator()
            metric = evaluator.create_aspect_metric(
                task_id=request.data.get("task_id"), 
                name=request.data.get('name'), 
                description=request.data.get('description')
            )
            
            serializer = AspectMetricSerializer(metric)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['get'])
    def aspect_metrics(self, request):
        """获取任务的所有评估指标"""
        try:
            evaluator = PromptEvaluator()
            metrics = evaluator.get_task_aspect_metrics(request.query_params.get('task_id'))
            serializer = AspectMetricSerializer(metrics, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['delete'])
    def delete_aspect_metric(self, request):
        """删除评估指标"""
        try:
            evaluator = PromptEvaluator()
            evaluator.delete_aspect_metric(request.query_params.get('metric_id'))
            return Response({'message': '删除成功'})
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def optimize_prompt(self, request):
        """自动优化Prompt"""
        try:
            optimizer = PromptOptimizer()
            result = optimizer.auto_optimize_prompt(request.data.get("evaluation_id"))
            return Response(result)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def optimize_suggest(self, request):
        """获取优化建议"""
        try:
            optimizer = PromptOptimizer()
            suggestions = optimizer.get_optimization_suggestions(request.data.get("evaluation_id"))
            return Response({'suggestions': suggestions})
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)