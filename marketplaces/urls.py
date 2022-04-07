from django.urls import path
from .views import (
    MarketplaceDetailView,
    MarketplacesList
)

urlpatterns = [
    path('marketplace/<str:unique_id>', MarketplaceDetailView.as_view(), name='marketplace_detail'),
    path('marketplaces/', MarketplacesList.as_view(), name='marketplaces')
]
