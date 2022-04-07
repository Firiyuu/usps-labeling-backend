from django.urls import path
from .views import (
    ZipLookupView,
    AddressLookupView
)

urlpatterns = [
    path('zip/', ZipLookupView.as_view(), name='get_zip_lookup'),
    path('address/', AddressLookupView.as_view(), name='get_address_lookup'),
]
