"""uwlapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

from core.views import (
    AddressBookView,
    LabelsView,
    LabelsViewGet,
    LabelsViewGetOne,
    LabelsPrintedView,
    RatesView,
    AddressValidationView,
    SquareCustomerList,
    SquareCustomerCardDetail,
    SquarePaymentView,
    SquareCustomerView,
    PrepayAccountDetail,
    PrepayHistoryDetail,
    ZoneView,
    SellerView,
    OrderView
)

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="UWL API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="info@unitedworldlogistics.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('marketplaces/', include('marketplaces.urls'), name='marketplaces'),
    path('accounts/', include('accounts.urls'), name='accounts'),
    path('api-auth/', include('rest_framework.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('addresses/', include('addresses.urls')),

    path('admin/', admin.site.urls),
    path('address/validate/', AddressValidationView.as_view(), name='validate_address'),
    path('create/labels/', LabelsView.as_view(), name='create_labels'),
    path('create/labels/<str:label_unique_id>/', LabelsView.as_view()),

    path('create/orders/', OrderView.as_view(), name='create_orders'),
    path('create/orders/<str:label_unique_id>/', OrderView.as_view()),



    path('get/labels/', LabelsViewGet.as_view(), name='get_labels'),
    path('get/labels/<int:pk>/', LabelsViewGetOne.as_view()),

    path('find/labels/', LabelsPrintedView.as_view(), name='find_labels'),
    path('shipping/rates/', RatesView.as_view(), name='get_rates'),
    path('api/token/', obtain_auth_token, name='obtain_token'),

    path('addressbook/', AddressBookView.as_view(), name='get_addressbook'),
    path('addressbook/<int:pk>/', AddressBookView.as_view()),

    path('zone/', ZoneView.as_view(), name='get_zone'),


    path('square/customers/', SquareCustomerList.as_view(), name='get_customers'),
    path('square/customer/', SquareCustomerView.as_view()),
    path('square/customer_card/', SquareCustomerCardDetail.as_view()), 
    path('square/payments/', SquarePaymentView.as_view(), name='create_sq_payments'),
    path('payments/', PrepayAccountDetail.as_view(), name='get_payments'),
    path('payments_history/', PrepayHistoryDetail.as_view(), name='get_payments_history'),

    path('create/vseller/', SellerView.as_view(), name='create_seller'),

    # TODO - Use this url for streaming PDF files
    path('find/labels/<str:tracking>', LabelsPrintedView.as_view(), name='view_pdf'),

    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api.json/', schema_view.without_ui(cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


]

urlpatterns = format_suffix_patterns(urlpatterns)
