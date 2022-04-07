from django.conf import settings
from django.http import Http404

# third part imports
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import (
    AddressBookSerializer,
    LabelsGeneralSerializer,
    LabelsGeneralSerializerGet,
    LabelsPrintedSerializer,
    AddressValidationSerializer,
    SquareCustomerInfoSerializer,
    SquareCardSerializer,
    PrepayAccountSerializer,
    PrepayHistorySerializer,
    ZoneSerializer,
    SellerCreateSerializer,
    SellerUserSerializer,
    OrderCreateSerializer,
    ItemSerializer
)
from .models import (
    Labels,
    LabelsPrinted,
    AddressBook,
    SquareCustomerInfo,
    SquareCard,
    PrepayAccount,
    PrepayHistory,
    UploadPrivate,
)

from .tasks import (
    create_labels,
    create_test_task
)

from django.core.files.base import ContentFile
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .utils.USPS_API import (
    USPSAPI
)

# Un Django
from datetime import datetime
import uuid
import pandas as pd
from decimal import Decimal
import requests
from random import choice
from string import ascii_uppercase
import logging

customers_api = settings.SQUARE_CLIENT.customers
payments_api = settings.SQUARE_CLIENT.payments

teaplix = settings.TEAPLIX_API

usps = USPSAPI()


class SellerView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = SellerUserSerializer

    def create_account(self, payload):
        uniqued_id = ''.join(choice(ascii_uppercase) for i in range(4))
        print(uniqued_id)
        try:
            # REQUEST HERE
            json_payload = {
                "VSAccountID": str(uniqued_id),
                "PartnerId": "LXPRESS",
                "Credentials": {
                    "SellerAccountIdentifier": payload['account_id'],
                    "AuthTokenOrPassword": payload['password']
                }
            }
            response = teaplix.post(data=json_payload, url_method="VSAccount")

            if response['Success']:
                # TODO
                # Assign to 'uniqued_id' user entity
                data = {
                    'vsaccount_id': uniqued_id,
                    'account_id': payload['account_id'],
                    'password': payload['password']
                }
                print(data)

                selleruser_serializer = SellerUserSerializer(data=data)
                if selleruser_serializer.is_valid():
                    print("Creation Success")
                    selleruser_serializer.save()
                    return "Seller Creation Success"
                return "Created but Failure on saving to DB"
        except Exception as e:
            logging.info(e)
            return str(response)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = SellerCreateSerializer(data=data)
        if serializer.is_valid():
            response = self.create_account(data)
            return Response(response)
        return Response(serializer.errors)


class OrderView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = SellerUserSerializer

    def create_order(self, payload):
        uniqued_id = ''.join(choice(ascii_uppercase) for i in range(4))
        try:

            date_today = datetime.today().strftime("%Y-%m-%d") 
            packges_dicts = []
            for i in range(0, len(payload["line_items"])):
                payload_packages = payload['line_items']
                packges_dict = {
                    "Weight": {
                        "Value": payload_packages[i]['weight'],
                        "Unit": payload['weight_unit']
                    },
                    "Dimensions": {
                        "Length": payload_packages[i]['dimensions_length'],
                        "Width": payload_packages[i]['dimensions_width'],
                        "Depth": payload_packages[i]['dimensions_depth'],
                        "Unit": payload_packages[i]['dimensions_unit'],
                    },
                    "IdenticalPackageCount": payload_packages[i]['identical_package'],
                    "Method": payload_packages[i]['method']
                }

                packges_dicts.append(packges_dict)

            item_dicts = []
            for i in range(0, len(payload["custom_items"])):
                payload_items = payload['custom_items']
                item_dict = {
                            "Name": payload_items[i]['customs_name'],
                            "Sku": payload_items[i]['customs_sku'],
                            "Description": payload_items[i]['customs_description'],
                            "Quantity": payload_items[i]['customs_quantity'],
                            "Amount": payload_items[i]['customs_amount'],
                            "Currency": payload_items[i]['customs_currency'],
                            "OriginCountry": payload_items[i]['customs_country'],
                            "TariffCode": payload_items[i]['tariff_code']
                }

                item_dicts.append(item_dict)

            json_payload = {
                "TxnId": payload['order_number'],
                "ShipDate": date_today,
                "From": {
                    "Name": payload['name'],
                    "Company": payload['company'],
                    "Street": payload['address1'],
                    "Street2": payload['address2'],
                    "State": payload['state'],
                    "City": payload['city'],
                    "ZipCode": payload['zipcode'],
                    "CountryCode": payload['country'],
                    "PhoneNumber": payload['phone'],
                    "Email": payload['email']
                    },
                "Packages": packges_dicts,
                "CustomsDeclaration": {
                    "Items": item_dicts,
                    "ReasonForExport": "Stockup"
                },
                "ImageFormat": {
                    "Layout": "4x6",
                    "Type": "PDF",
                    "LabelReturn": "URL"
                    },
                "IsReturn": False,
                "Provider": "GSS"
            }
            response = teaplix.post(
                data=json_payload,
                url_method="PurchaseLabelForOrder"
            )
            if "ClientRequestId" in response:
                return True, response
            else:
                return False, response

        except Exception as e:
            print(e)
            return str(response)

    def post(self, request, *args, **kwargs):
        data = request.data
        data["user"] = self.request.user.id
        serializer = OrderCreateSerializer(data=data)
        if serializer.is_valid():
            response_status, status = self.create_order(request.data)
            if not response_status:
                return Response(status)

            self.save_tracking(status, uuid_gen)
            serializer.save()
            data = {
                'label': serializer.data,
                'tracking': status
            }
            return Response(data)
        return Response(serializer.errors)


class LabelsView(APIView):
    permission_classes = (IsAuthenticated, )


    def get_object(self, label_unique_id):
        try:
            return Labels.objects.get(
                label_unique_id=label_unique_id,
                is_archived=False
            )
        except Labels.DoesNotExist:
            raise Http404

    def cancel_label(self, pk):
        try:

            # TODO -- Initiate user ownership
            # printed_label = LabelsPrinted.objects.get(
            #     label_id=pk,
            #     user=self.request.user
            #     )

            request_keys = {
                "packageId": str(pk)
            }

            return usps.cancel_label(request_keys)

            usps.post(data=request_keys, )

            return teaplix.post(data=request_keys, url_method="CancelLabel")

        except LabelsPrinted.DoesNotExist:
            raise Http404

    # Uncomment when---
    #  def get(self, request, *args, **kwargs):
    #     qs = Labels.objects.all()
    #     serializer = LabelsGeneralSerializer(qs, many=True)
    #     return Response(serializer.data)

    def create_labels(self, payload):

        try:
            uuid_gen = uuid.uuid4()

            # REQUEST HERE
            date_today = datetime.today().strftime("%Y-%m-%d") 
            packges_dicts = []
            for i in range(0, len(payload["packages"])):
                payload_packages = payload['packages']

                if payload_packages[i]['reference'] == "":
                    reference_var =   str(uuid_gen) + str(i)
                else:
                    reference_var = payload_packages[i]['reference']

                packges_dict =  {
                    "Weight": {
                        "Value": payload_packages[i]['weight_value'],
                        "Unit": payload_packages[i]['weight_unit']
                    },
                    "Dimensions": {
                        "Length":payload_packages[i]['dimensions_length'],
                        "Width":payload_packages[i]['dimensions_width'],
                        "Depth":payload_packages[i]['dimensions_depth'],
                        "Unit": payload_packages[i]['dimensions_unit'],
                    },
                    "Reference":  reference_var,
                    "Method": payload_packages[i]['method'],
                }

                packges_dicts.append(packges_dict)
            
            json_payload = {
                "ClientRequestId": str(uuid_gen),
                "ShipDate": str(date_today),
                "From":{
                    "Name": payload['sender_name'],
                    "Company": payload['sender_company'],
                    "Street": payload['sender_address1'],
                    "Street2": payload['sender_address2'],
                    "State": payload['sender_state'],
                    "City":  payload['sender_city'],
                    "ZipCode": payload['sender_zip'],
                    "CountryCode": payload['sender_country_code'],
                    "Country": payload['sender_country'],
                    "PhoneNumber":payload['sender_phone'],
                    "Email": payload['sender_email']
                },
                "To": {
                    "Name": payload['receiver_name'],
                    "Company": payload['receiver_company'],
                    "Street": payload['receiver_address1'],
                    "Street2": payload['receiver_address2'],
                    "State": payload['receiver_state'],
                    "City": payload['receiver_city'],
                    "ZipCode": payload['receiver_zip'],
                    "Country": payload['receiver_country'],
                    "CountryCode": payload['receiver_country_code'],
                    "PhoneNumber": payload['receiver_phone'],
                    "Email": payload['receiver_email']
                },
                "Packages": packges_dicts,
                "ImageFormat": {
                    "Layout":  payload['packages'][0]['imgformat_layout'],
                    "Type":  payload['packages'][0]['imgformat_type'],
                    "LabelReturn":  payload['packages'][0]['imgformat_labelreturn'],
                },
                "IsReturn": payload['packages'][0]['is_return'],
                "Provider":  payload['packages'][0]['provider']
            }

            response = teaplix.post(data=json_payload, url_method="PurchaseLabel")

            if "ClientRequestId" in response:
                return True, response
            else:

                return False, response

        except Exception as e:
            return False, str(e)


    def save_tracking(self, json_format, label_id):

        data = {
            'label_id': str(label_id),
            'clientrequest_id': str(json_format['ClientRequestId']),
            'trackinginfo_number':  str(json_format['TrackingInfo'][0]['TrackingNumber']),
            'trackinginfo_carriername':   str(json_format['TrackingInfo'][0]['CarrierName']),
            'labeldata_type':  str(json_format['LabelData'][0]['Type']),
            'labeldata_content': str(json_format['LabelData'][0]['Content']),
            'success': json_format['Success'],
            'code':  int(json_format['Code']),
            'message':  str(json_format['Message']),
            'provider':  str(json_format['Provider']),
            'user': self.request.user.id
        }

        savedtracking_serializer = LabelsPrintedSerializer(data=data)
        if savedtracking_serializer.is_valid():
            savedtracking_serializer.save()



    def post(self, request, *args, **kwargs):
        uuid_gen = uuid.uuid4()
        data = request.data
        data["label_unique_id"] = str(uuid_gen)
        data["user"] = self.request.user.id

        serializer = LabelsGeneralSerializer(data=data)

        if serializer.is_valid():
            # task = create_labels.delay(request.data, uuid_gen)
            # response_status, status = self.create_labels(data)
            response_status = usps.create_labels(data, data["user"])
            return Response(response_status)
            if not response_status:
                return Response(status)


            serializer.save()
            data = {
                'label': serializer.data,
                # 'task_id': task.id,
                'tracking': status
            }
            return Response(data)
        return Response(serializer.errors)

    def delete(self, request, label_unique_id, format=None):

        # TODO -- Uncomment for user ownership @joeper

        # label = self.get_object(label_unique_id)
        # try:
        #     payment_history = PrepayHistory.objects.get(
        #         payment_id=label.label_unique_id
        #         )
        # except PrepayHistory.DoesNotExist:
        #     payment_history = None

        # if not payment_history:
        #     if self.cancel_label(label_unique_id):
        #         response = {
        #             "status": "Success in deleting label_id: " + str(label.label_unique_id)
        #         }
        #         label.is_archived = True
        #         label.save()
        #         return Response(response)
        #     else:
        #         response = {"status": "failed to delete label"}
        #         return Response(response, status=status.HTTP_400_BAD_REQUEST)

        response =  self.cancel_label(label_unique_id)
        if response:
            # TODO -- Uncomment for user ownership @joeper

            # refund_amount = payment_history.amount
            # account = PrepayAccount.objects.get(user=request.user)
            # new_balance = round(account.balance + refund_amount, 2)

            # history_data = {
            #     'user': self.request.user.id,
            #     'detail': 'Refund payment on cancel label',
            #     'payment_id': label.label_unique_id,
            #     'amount': refund_amount,
            #     'prev_balance': account.balance,
            #     'new_balance': new_balance,
            #     'payment_method': 'USPS Balance',
            # }

            # account_data = {
            #     'user': self.request.user.id,
            #     'balance': new_balance
            # }

            # account_serializer = PrepayAccountSerializer(
            #     account,
            #     data=account_data
            # )
            # history_serializer = PrepayHistorySerializer(data=history_data)

            # if not account_serializer.is_valid():
            #     return Response(account_serializer.errors)
            # if not history_serializer.is_valid():
            #     return Response(history_serializer.errors)

            # label.is_archived = True
            # label.save()

            # payment_history.is_archived = True
            # payment_history.save()

            # account_serializer.save()
            # history_serializer.save()
            # response = {
            #     "status": "Success in deleting label_id: " + str(label.label_unique_id),
            #     "refunded": "refund amount: " + str(payment_history.amount)
            # }
            return Response(response)
        else:
            response = {"status": "failed to delete label"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class LabelsViewGet(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        qs = Labels.objects.filter(user=self.request.user, is_archived=False)
        serializer = LabelsGeneralSerializerGet(qs, many=True)
        return Response(serializer.data)


class LabelsViewGetOne(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self, pk):
        try:
            return Labels.objects.filter(pk=pk, is_archived=False)
        except Labels.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        qs = self.get_object(pk)
        serializer = LabelsGeneralSerializerGet(qs, many=True)
        return Response(serializer.data)


class ZoneView(APIView):
    permission_classes = (IsAuthenticated, )

    def find_zone(self, payload):

        json_payload = {
            "Routes": [{
                "FromZip": payload['from_zip'],
                "ToZip": payload['to_zip']
            }]
        }

        return teaplix.post(data=json_payload, url_method="Zones")

    def post(self, request, *args, **kwargs):

        data = request.data
        serializer = ZoneSerializer(data=data)

        if serializer.is_valid():
            response = self.find_zone(request.data)
            if response:
                return Response(response["Routes"][0]["Zone"])
        return Response(serializer.errors)


class AddressValidationView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressValidationSerializer

    def validate_address(self, payload):
        json_payload = {
            "Address": {
                "Street": payload['address_street'],
                "Street2":  payload['address_street2'],
                "City":  payload['address_city'],
                "State":  payload['address_state'],
                "ZipCode":  payload['address_zip'],
                "Country":  'United States',
                "CountryCode": "US"
            },
            "Provider": "UPS"
        }

        return teaplix.post(data=json_payload, url_method="AddressValidation")

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = AddressValidationSerializer(data=data)
        if serializer.is_valid():
            response = self.validate_address(request.data)
            return Response(response)
        return Response(serializer.errors)


class LabelsPrintedView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = LabelsPrintedSerializer

    def get_payment(self, label_id):
        try:
            return PrepayHistory.objects.get(
                payment_id=label_id,
                is_archived=False
            )
        except PrepayHistory.DoesNotExist:
            return None

    def get_object(self, file_name, user_id):
        try:
            return UploadPrivate.objects.get(file=file_name, user=user_id)
        except UploadPrivate.DoesNotExist:
            return None

    def get(self, request, tracking, *args, **kwargs):
        qs = LabelsPrinted.objects.get(label_id=tracking)
        serializer = LabelsPrintedSerializer(qs, many=False)
        data = serializer.data
        content = data["labeldata_content"]
        filename = data["trackinginfo_number"] + '.pdf'
        pdf_file = self.get_object(filename, request.user.id)

        if not pdf_file:
            r = requests.get(content,  headers={"APIToken": settings.TEAPPLIX_API_TOKEN}, allow_redirects=True)
            pdf_file = UploadPrivate(user=request.user)
            pdf_file.file.save(filename, ContentFile(r.content))
            pdf_file.save()

        return Response({'file_url': pdf_file.file.url})

    def post(self, request, *args, **kwargs):
        data = request.data
        qs = LabelsPrinted.objects.get(label_id=data["label_unique_id"])
        ps = self.get_payment(data["label_unique_id"])
        serializer = LabelsPrintedSerializer(qs, many=False)
        data = serializer.data
        if ps:
            ps_serializer = PrepayHistorySerializer(ps)
            ps_serializer.data
            data = {
                "label_data": serializer.data,
                "payment_data": ps_serializer.data
            }
        return Response(data)


class AddressBookView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = AddressBookSerializer

    def get_object(self, pk):
        try:
            return AddressBook.objects.get(pk=pk, is_archived=False)
        except AddressBook.DoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        qs = AddressBook.objects.filter(
            user=self.request.user,
            is_archived=False
        )
        serializer = AddressBookSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = AddressBookSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response("Success in saving to address book.")
        return Response(serializer.errors)

    def put(self, request, pk, format=None):
        adbook = self.get_object(pk)
        serializer = AddressBookSerializer(adbook, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        adbook = self.get_object(pk)
        adbook.is_archived = True
        adbook.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RatesView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        data = request.data
        carrier = data["carrier_name"]
        csv_to_read = ''
        if carrier == "priority-mail-express":
            csv_to_read = 'core/resources/Commercial_Plus_Priority_Mail_PRICES.csv'
        elif carrier == "first-class-mail-parcel":
            csv_to_read = 'core/resources/First_Class_Mail_PARCEL_Commercial_Prices.csv'
        elif carrier == "commercial-plus-priority":
            csv_to_read = 'core/resources/Priority_Mail_EXPRESS_Commercial_Plus_Pricing.csv'
        else:
            return Response('Carrier is invalid')
        dataframe = pd.read_csv(csv_to_read)
        headers = list(dataframe.columns.values)
        # oz and lb
        unit = data["unit"]
        value = data["value"]
        zone = data["zone"]
        unit_compute = headers[0]
        if zone == "1" or zone == "2":
            zone = "1 & 2"
        try:
            df_loc = dataframe.loc[dataframe[unit_compute] == float(value)]
            found = df_loc[zone].values
            response = {
                "shipping_rate": found[0]
            }
            return Response(response)
        # TODO-Find Specific Combination Invalid
        except Exception as e:
            return Response('Combination invalid')


class SquareCustomerList(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = SquareCustomerInfoSerializer

    def get(self, request, format=None):
        result = customers_api.list_customers()
        if result.is_success():
            return Response(result.body)
        elif result.is_error():
            return Response(result.errors)

    def create_customer(self, payload):
        result = customers_api.create_customer(payload)

        if result.is_success():
            return result.body
        elif result.is_error():
            return Response(result.errors)

    def post(self, request, *args, **kwargs):
        # TODO: Use authentication and user model to get User Info
        data = {}
        square_data = self.create_customer(request.data)
        if 'customer' not in square_data:
            return square_data

        data['customer_id'] = square_data['customer']['id']
        data['user'] = self.request.user.id
        serializer = SquareCustomerInfoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class SquareCustomerView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self, user_id, format=None):
        try:
            return SquareCustomerInfo.objects.get(user=user_id)
        except SquareCustomerInfo.DoesNotExist:
            raise Http404

    def get_square_object(self, customer_id, format=None):
        result = customers_api.retrieve_customer(customer_id)
        if result.is_success():
            return result.body
        elif result.is_error():
            raise Http404

    def get(self, request, *args, **kwargs):
        customer = self.get_object(self.request.user.id)
        return Response(self.get_square_object(customer.customer_id))

    def put(self, request, customer_id, format=None):
        result = customers_api.update_customer(customer_id, request.data)

        if result.is_success():
            return Response(result.body)
        elif result.is_error():
            return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        customer = self.get_object(self.request.user.id)
        result = customers_api.delete_customer(customer.customer_id)

        if result.is_success():
            customer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif result.is_error():
            return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)


class SquareCustomerCardDetail(APIView):
    permission_classes = (IsAuthenticated, )

    def create_customer(self, user):
        payload = {
            'given_name': user.first_name,
            'family_name': user.last_name,
            'email_address': user.email
        }
        result = customers_api.create_customer(payload)

        if result.is_success():
            return result.body
        elif result.is_error():
            return Response(result.errors)

    def get_customer(self, user, format=None):
        try:
            return SquareCustomerInfo.objects.get(user=user.id)
        except SquareCustomerInfo.DoesNotExist:
            return self.create_customer(user)

    def get_object(self, pk):
        try:
            return SquareCard.objects.get(pk=pk)
        except SquareCard.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        customer = self.get_customer(self.request.user)
        square_card = self.get_object(customer.id)
        serializer = SquareCardSerializer(square_card)
        return Response(serializer.data)

    def create_customer_card(self, customer_id, payload):
        result = customers_api.create_customer_card(customer_id, payload)

        if result.is_success():
            return result.body
        elif result.is_error():
            return Response(result.errors)

    def post(self, request, *args, **kwargs):
        customer = self.get_customer(self.request.user)
        data = {}
        square_data = self.create_customer_card(
            customer.customer_id,
            request.data
        )
        if 'card' not in square_data:
            return square_data

        data['card_id'] = square_data['card']['id']
        data['customer'] = customer.id
        serializer = SquareCardSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, *args, **kwargs):
        customer = self.get_customer(self.request.user)
        result = customers_api.delete_customer_card(
            customer.customer_id,
            request.data['card_id']
        )
        if result.is_success():
            card = SquareCard.objects.get(card_id=request.data['card_id'])
            card.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif result.is_error():
            return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)


class SquarePaymentView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_customer(self, user_id, format=None):
        try:
            return SquareCustomerInfo.objects.get(user=user_id)
        except SquareCustomerInfo.DoesNotExist:
            raise Http404

    def get_or_none(self, classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None

    def cents_to_dollar(self, cents):
        cents_to_dollars_format_string = '{:,.2f}'
        return cents_to_dollars_format_string.format(10*cents/100.0)

    def create_payment(self, customer, idempotency_key, payload):
        payload['idempotency_key'] = idempotency_key
        payload['customer_id'] = customer.customer_id
        result = payments_api.create_payment(payload)

        if result.is_success():
            return result.body
        elif result.is_error():
            return result.errors

    def post(self, request, *args, **kwargs):
        customer = self.get_customer(self.request.user.id)
        idempotency_key = str(uuid.uuid4())
        square_data = self.create_payment(customer, idempotency_key, request.data)
        if 'payment' not in square_data:
            return Response(square_data)

        customer_account = self.get_or_none(
            PrepayAccount,
            user=self.request.user
        )
        payment_result = square_data['payment']
        amount_money = Decimal(payment_result['amount_money']['amount'] / 100)
        new_balance = amount_money if customer_account is None else customer_account.balance + amount_money
        amount_money = round(amount_money, 2)
        new_balance = round(new_balance, 2)
        history_data = {
            'user': self.request.user.id,
            'detail': 'Add amount to prepay account',
            'amount': amount_money,
            'prev_balance': 0.00 if customer_account is None else customer_account.balance,
            'new_balance': new_balance,
            'payment_method': payment_result['source_type'],
            'idempotency_key': idempotency_key,
            'payment_id': payment_result['id'],
            'source_id': request.data['source_id']
        }

        history_serializer = PrepayHistorySerializer(data=history_data)

        if not history_serializer.is_valid():
            return Response(history_serializer.errors)

        if customer_account is None:
            customer_account = PrepayAccount(
                user=self.request.user,
                balance=amount_money,
            )
        else:
            customer_account.balance = new_balance

        history_serializer.save()
        customer_account.save()

        return Response(square_data)


class PrepayAccountDetail(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self, user):
        try:
            return PrepayAccount.objects.get(user=user)
        except PrepayAccount.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        # Todo: change customer_id with authenticated user
        prepay_account = self.get_object(self.request.user)
        serializer = PrepayAccountSerializer(prepay_account)
        return Response(serializer.data)

    def post(self, request):
        account = self.get_object(self.request.user)
        if not request.data['label_unique_id']:
            return Response('label_unique_id is requred')

        amount_money = request.data['amount_money']
        payment_amount = round(Decimal(amount_money['amount'] / 100), 2)
        if account.balance <= 0 or account.balance < payment_amount:
            msg = {
                "error": "Insuficient balance",
                "balance": account.balance,
                "payment_amount": amount_money['amount'],
            }
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        new_balance = round(account.balance - payment_amount, 2)
        history_data = {
            'user': self.request.user.id,
            'detail': request.data['detail'],
            'payment_id': request.data['label_unique_id'],
            'amount': payment_amount,
            'prev_balance': account.balance,
            'new_balance': new_balance,
            'payment_method': 'USPS Balance',
        }

        account_data = {
            'user': self.request.user.id,
            'balance': new_balance
        }

        serializer = PrepayAccountSerializer(account, data=account_data)
        if not serializer.is_valid():
            return Response(serializer.errors)

        serializer.save()

        history_serializer = PrepayHistorySerializer(data=history_data)
        if history_serializer.is_valid():
            history_serializer.save()
            return Response(history_serializer.data)
        return Response(
            history_serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class PrepayHistoryDetail(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self, user):
        try:
            return PrepayHistory.objects.filter(user=user, is_archived=False)
        except PrepayHistory.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        # Todo: change customer_id with authenticated user
        square_card = self.get_object(self.request.user)
        serializer = PrepayHistorySerializer(square_card, many=True)
        return Response(serializer.data)
