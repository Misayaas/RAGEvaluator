## 提供RAG评估相关的API接口

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.evaluation import RAGEvaluation, EvaluationResult
from datetime import datetime
from ..serializers import RAGEvaluationSerializer

class RAGEvaluationViewSet(viewsets.GenericViewSet):
    queryset = RAGEvaluation.objects.all()
    serializer_class = RAGEvaluationSerializer
    
    @action(detail=False, methods=['post'])
    def create_evaluation(self, request):
        # 设置为当前日期
        request.data['created_at'] = datetime.now().isoformat()
        serializer = RAGEvaluationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def upload_evaluation_file(self, request, id=None):
        # 上传评估数据文件的逻辑
        # 根据 pk 获取对应的评估任务，处理文件上传
        return Response({'message': 'Evaluation file uploaded successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def start_evaluation(self, request, id=None):
        # 开启一轮评估的逻辑
        # 根据 pk 获取对应的评估任务，进行评估处理
        return Response({'message': 'Evaluation started successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def calculate_metrics(self, request, id=None):
        # 计算评估指标的逻辑
        # 根据 pk 获取对应的评估任务，计算指标并存储
        return Response({'message': 'Metrics calculated and stored successfully'}, status=status.HTTP_200_OK)
