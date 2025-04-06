from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromptTemplateViewSet, PromptEvaluationViewSet

router = DefaultRouter()
router.register(r'templates', PromptTemplateViewSet)
router.register(r'evaluations', PromptEvaluationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]