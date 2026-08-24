from django.urls import path
from .views import AnalyzeLeafView, ScanHistoryListView, DiseaseKnowledgeListView

urlpatterns = [
    path('analyze/', AnalyzeLeafView.as_view(), name='analyze-leaf'),
    path('history/', ScanHistoryListView.as_view(), name='scan-history'),
    path('knowledge/', DiseaseKnowledgeListView.as_view(), name='disease-knowledge'),
]
