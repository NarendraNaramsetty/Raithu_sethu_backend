from django.urls import path
from .views import GovtSchemeListView, GovtSchemeDetailView

urlpatterns = [
    path('', GovtSchemeListView.as_view(), name='schemes-list'),
    path('<int:pk>/', GovtSchemeDetailView.as_view(), name='scheme-detail'),
]
