from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from django.utils.translation import ugettext_lazy as _
from rest_auth.registration.serializers import VerifyEmailSerializer
from rest_framework import status
from rest_framework.decorators import api_view, APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view()
def django_rest_auth_null():
    return Response(status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)

    def get_serializer(self, *args, **kwargs):
        return VerifyEmailSerializer(*args, **kwargs)

    def get(self, request, key, *args, **kwargs):
        self.key = key
        try:
            confirmation = self.get_object()
            confirmation.confirm(self.request)
            return Response(
                {'detail': _('Successfully confirmed email.')},
                status=status.HTTP_200_OK
            )
        except EmailConfirmation.DoesNotExist:
            return Response(
                {'detail': _('Error. Incorrect key.')},
                status=status.HTTP_404_NOT_FOUND
            )

    def get_object(self, queryset=None):
        key = self.key
        emailconfirmation = EmailConfirmationHMAC.from_key(key)
        if not emailconfirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                emailconfirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                raise EmailConfirmation.DoesNotExist
        return emailconfirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs
