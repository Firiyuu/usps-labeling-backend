from django.urls import path, include
from rest_framework import routers
from django.conf.urls import url
from accounts.views import django_rest_auth_null, VerifyEmailView
from django.urls import re_path

urlpatterns = [
    path('registration/', include('rest_auth.registration.urls')),
    path('rest-auth/registration/account-email-verification-sent/', django_rest_auth_null, name='account_email_verification_sent'),
    path('password-reset/confirm/<str:uidb64>)/<str:token>/', django_rest_auth_null, name='password_reset_confirm'),
    re_path('rest-auth/registration/account-confirm-email/(?P<key>.+)/', VerifyEmailView.as_view(), name='account_confirm_email'),
]
