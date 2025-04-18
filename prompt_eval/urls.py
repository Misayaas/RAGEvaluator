from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromptEvaluationViewSet

router = DefaultRouter()
router.register(r'evaluations', PromptEvaluationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
