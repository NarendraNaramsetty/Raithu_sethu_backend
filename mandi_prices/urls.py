from django.urls import path
from .views import MandiPriceListView, MandiPriceSummaryView, MandiFilterOptionsView

urlpatterns = [
    path('', MandiPriceListView.as_view(), name='mandi-prices-list'),
    path('summary/', MandiPriceSummaryView.as_view(), name='mandi-prices-summary'),
    path('filters/', MandiFilterOptionsView.as_view(), name='mandi-prices-filters'),
]
