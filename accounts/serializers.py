from django.conf import settings
from django.http import Http404
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from allauth.account import app_settings as allauth_settings
from allauth.utils import email_address_exists
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from core.serializers import (
    SquareCustomerInfoSerializer,
    SellerUserSerializer,
)
from accounts.models import (
    User
)
from random import choice
from string import ascii_uppercase
teaplix = settings.TEAPLIX_API
customers_api = settings.SQUARE_CLIENT.customers

import re
regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


class UWLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = 'Must include "username" and "password".'
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = str(attrs.get('username')).lower()
        password = attrs.get('password')

        user = None

        if(re.search(regex, username)):
            user = User.objects.get(email=username)
            user = self._validate_username(user.username, password)
        else:
            user = self._validate_username(username, password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = 'User account is disabled.'
                raise exceptions.ValidationError(msg)
        else:
            msg = 'Unable to log in with provided credentials.'
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError('E-mail is not verified.')

        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    username = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)
    company = serializers.CharField(required=False, write_only=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    ("A user is already registered with this e-mail address."))
        return email

    def validate_username(self, username):
        try:
            username = User.objects.get(username=username)
            raise serializers.ValidationError(
                    ("A user is already registered with this username."))
        except User.DoesNotExist:
            return username

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                ("The two password fields didn't match."))
        return data

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'username': self.validated_data.get('username', ''),
            'company': self.validated_data.get('company', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
        }

    def create_square_customer(self, user):
        payload = {
            'given_name': user.first_name,
            'family_name': user.last_name,
            'email_address': user.email,
        }
        square_data = customers_api.create_customer(payload)
        if square_data.is_success():
            user_data = {
                'customer_id': square_data.body['customer']['id'],
                'user': user.id
            }

            serializer = SquareCustomerInfoSerializer(data=user_data)
            if serializer.is_valid():
                serializer.save()
                return True
            else:
                raise Http404
        else:
            raise Http404

    def create_seller_account(self, user):
        uniqued_id = ''.join(choice(ascii_uppercase) for i in range(4))
        # REQUEST HERE
        json_payload = {
            "VSAccountID": str(uniqued_id),
            "PartnerId": "LXPRESS",
            "Credentials": {
                "SellerAccountIdentifier": user.username,
                "AuthTokenOrPassword": user.password
            }
        }
        response = teaplix.post(data=json_payload, url_method="VSAccount")

        if response['Success']:
            data = {
                'user': user.id,
                'vsaccount_id': uniqued_id,
                'account_id': user.username,
                'password': user.password
            }
            selleruser_serializer = SellerUserSerializer(data=data)
            if selleruser_serializer.is_valid():
                selleruser_serializer.save()
                return "Seller Creation Success"
            raise Http404
        else:
            raise Http404

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)

        self.create_square_customer(user)
        self.create_seller_account(user)

        setup_user_email(request, user, [])
        user.save()
        return user
