from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/prompt-eval/', include('prompt_eval.urls')),
    path('api/rag-eval/', include('rag_eval.urls')),
]
