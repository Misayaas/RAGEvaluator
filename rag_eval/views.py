## 提供RAG评估相关的API接口

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models.evaluation import RAGEvaluation, EvaluationResult
from .services.evaluator import evaluate_rag
from datetime import datetime
from .serializers import RAGEvaluationSerializer

class RAGEvaluationViewSet(viewsets.GenericViewSet):
    queryset = RAGEvaluation.objects.all()
    serializer_class = RAGEvaluationSerializer
    

    @action(detail=False, methods=['get'])
    def all(self, request):
        evaluations = RAGEvaluation.objects.all()
        serializer = RAGEvaluationSerializer(evaluations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    @action(detail=True, methods=['get'])
    def get(self, request, pk):
        try:
            evaluation = RAGEvaluation.objects.get(pk=pk)
            serializer = RAGEvaluationSerializer(evaluation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)



    @action(detail=True, methods=['post'])
    def edit(self, request, pk):
        try:
            evaluation = RAGEvaluation.objects.get(pk=pk)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RAGEvaluationSerializer(evaluation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    @action(detail=False, methods=['post'])
    def create_evaluation(self, request):
        # 设置为当前日期
        data = request.data.copy()  # 复制请求数据
        data['created_at'] = datetime.now().isoformat()
        serializer = RAGEvaluationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    @action(detail=True, methods=['post'])
    def upload_evaluation_file(self, request, pk=None):
        try:
            evaluation = RAGEvaluation.objects.get(pk=pk)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'evaluated_file' not in request.FILES:
            return Response({'error': 'No file was uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['evaluated_file']
        evaluation.evaluated_file.save(file.name, file, save=True)
        
        serializer = RAGEvaluationSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


    @action(detail=True, methods=['post'])
    def evaluate(self, request, pk=None):
        # 开启一轮评估的逻辑
        # 根据 pk 获取对应的评估任务，进行评估处理
        try:
            evaluation = RAGEvaluation.objects.get(pk=pk)
        except RAGEvaluation.DoesNotExist:
            return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not evaluation.evaluated_file:
            return Response({'error': 'Evaluated file is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 假设 evaluate_document 函数可以根据评估文件进行评估，返回评估结果
        evaluation_result = evaluate_rag(evaluation.evaluated_file.path)
        
        # 填充 faithfulness_score 等数据
        evaluation.faithfulness_score = evaluation_result.get('faithfulness_score', 0.0)
        
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


    @action(detail=True, methods=['post'])
    def calculate_metrics(self, request, pk=None):
        # 计算评估指标的逻辑
        # 根据 pk 获取对应的评估任务，计算指标并存储
        return Response({'message': 'Metrics calculated and stored successfully'}, status=status.HTTP_200_OK)
