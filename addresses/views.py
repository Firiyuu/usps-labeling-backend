from django.conf import settings
from django.http import Http404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render

from smartystreets_python_sdk.us_zipcode import Lookup as ZIPCodeLookup
from smartystreets_python_sdk.us_autocomplete import Lookup as AutocompleteLookup, geolocation_type
from smartystreets_python_sdk import exceptions

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .utils import SmartyStreetsAPI


class ZipLookupView(APIView):
    permission_classes = (IsAuthenticated, )
    zip_code_param = openapi.Parameter(
        'zip_code', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[zip_code_param])
    def post(self, request, *args, **kwargs):
        lookup = ZIPCodeLookup()
        lookup.zipcode = request.data['zip_code']
        try:
            settings.SMARTYSTREETS_ZIP_CLIENT.send_lookup(lookup)
        except exceptions.SmartyException as err:
            return Response(err)

        result = lookup.result
        zipcodes = result.zipcodes
        cities = result.cities
        result = {
            'cities': [],
            'zip_codes': []
        }
        for city in cities:
            result['cities'].append({
                'city': city.city,
                'state': city.state,
                'mailable_city': city.mailable_city
            })

        for zipcode in zipcodes:
            result['zip_codes'].append({
                'zip_code': zipcode.zipcode
            })

        return Response(result)

class AddressLookupView(APIView):
    address1_param = openapi.Parameter(
        'address1', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[address1_param])
    def post(self, request, *args, **kwargs):
        smarty = SmartyStreetsAPI()
        if 'selected' in request.data:
            lookup = smarty.get(request.data['address1'], request.data['selected'])
        else:
            lookup = smarty.get(request.data['address1'])

        return Response(lookup)
