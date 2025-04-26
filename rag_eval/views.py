## 提供RAG评估相关的API接口

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models.evaluation import RAGEvaluation, EvaluationResult
from .models.task import RAGTask
from .services.evaluator import evaluate_rag
from datetime import datetime
from .serializers import RAGEvaluationSerializer, RAGTaskSerializer

class RAGEvaluationViewSet(viewsets.GenericViewSet):
    queryset = RAGEvaluation.objects.all()
    serializer_class = RAGEvaluationSerializer
    

    @action(detail=False, methods=['get'])
    def all_eval(self, request):
        evaluations = RAGEvaluation.objects.all()
        serializer = RAGEvaluationSerializer(evaluations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    @action(detail=False, methods=['get'])
    def all_task(self, request):
        evaluations = RAGTask.objects.all()
        serializer = RAGTaskSerializer(evaluations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['get'])
    def get_eval(self, request):
        try:
            pk = request.GET.get('id')
            evaluation = RAGEvaluation.objects.get(pk=pk)
            serializer = RAGEvaluationSerializer(evaluation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=['get'])
    def get_task(self, request):
        try:
            pk = request.GET.get('id')
            evaluation = RAGTask.objects.get(pk=pk)
            serializer = RAGTaskSerializer(evaluation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)



    @action(detail=False, methods=['post'])
    def edit_eval(self, request):
        try:
            pk = request.data.get('id')
            evaluation = RAGEvaluation.objects.get(pk=pk)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RAGEvaluationSerializer(instance=evaluation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def edit_task(self, request):
        try:
            pk = request.data.get('id')
            task = RAGTask.objects.get(pk=pk)
        except RAGTask.DoesNotExist:
            return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RAGTaskSerializer(instance=task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'])
    def add_eval(self, request):
        try:
            data = request.data.copy()  # 复制请求数据
            data['task'] = data['task_id']
            data['created_at'] = datetime.now().isoformat()
            serializer = RAGEvaluationSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    

    @action(detail=False, methods=['post'])
    def create_task(self, request):
        # 设置为当前日期
        data = request.data.copy()  # 复制请求数据
        data['created_at'] = datetime.now().isoformat()
        data['updated_at'] = datetime.now().isoformat()
        serializer = RAGTaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['delete'])
    def delete_eval(self, request):
        try:
        # 根据评估任务的 ID 从数据库中获取要删除的评估任务
            pk = request.query_params.get('id')
            evaluation = RAGEvaluation.objects.get(pk=pk)
            evaluation.delete()
            return Response({"deleted"}, status=status.HTTP_200_OK)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)



    @action(detail=False, methods=['delete'])
    def delete_task(self, request):
        try:
        # 根据评估任务的 ID 从数据库中获取要删除的评估任务
            pk = request.query_params.get('id')
            task = RAGTask.objects.get(pk=pk)
            task.delete()
            return Response({"deleted"}, status=status.HTTP_200_OK)
        except RAGTask.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)



    @action(detail=False, methods=['post'])
    def upload_evaluation_file(self, request):
        try:
            pk = int(request.data.get('id'))
            evaluation = RAGEvaluation.objects.get(pk=pk)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'evaluated_file' not in request.FILES:
            return Response({'error': 'No file was uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['evaluated_file']
        evaluation.evaluated_file.save(file.name, file, save=True)
        
        serializer = RAGEvaluationSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


    @action(detail=False, methods=['get'])
    def evaluate(self, request):
        # 开启一轮评估的逻辑
        # 根据 pk 获取对应的评估任务，进行评估处理
        try:
            pk = request.GET.get('id')
            evaluation = RAGEvaluation.objects.get(pk=pk)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not evaluation.evaluated_file:
            return Response({'error': 'Evaluated file is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 评估
        evaluation_result = evaluate_rag(evaluation.evaluated_file.path)
        
        # 填充 faithfulness_score 等数据
        evaluation.faithfulness_score = evaluation_result.get('faithfulness_score', 0.0)
        evaluation.context_recall_score = evaluation_result.get('context_recall_score', 0.0)
        evaluation.context_precision_score = evaluation_result.get('context_precision_score', 0.0)
        
        # 保存评估任务对象
        evaluation.save()
        
        # 创建 EvaluationResult 对象保存详细评估指标
        EvaluationResult.objects.create(
            evaluation=evaluation,
            metric_name='faithfulness_score',
            metric_value=evaluation.faithfulness_score,
            metric_details=evaluation_result  # 假设评估结果中包含详细信息
        )
        
        serializer = RAGEvaluationSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)
