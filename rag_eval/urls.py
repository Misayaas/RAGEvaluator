from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RAGEvaluationViewSet

router = DefaultRouter()
router.register(r'evaluations', RAGEvaluationViewSet, basename='evaluations')

urlpatterns = [
    path('', include(router.urls)),
]
