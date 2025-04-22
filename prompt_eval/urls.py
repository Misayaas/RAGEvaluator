from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromptEvaluationViewSet

router = DefaultRouter()
router.register(r'evaluations', PromptEvaluationViewSet, basename='evaluations')

app_name = 'prompt_eval'

urlpatterns = [
    path('', include(router.urls)),
]
