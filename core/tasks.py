from celery import shared_task
from django.conf import settings
from datetime import datetime
from .models import (
    LabelStatus,
    UploadPrivate
)
from .serializers import (
    LabelsPrintedSerializer
)

import requests
import uuid
import time

teaplix = settings.TEAPLIX_API

@shared_task
def add(x, y):
    return x + y

@shared_task
def create_test_task():
    time.sleep(int(1) * 10)
    return True, "test"

def get_object(file_name):
        try:
            return UploadPrivate.objects.get(file=file_name)
        except UploadPrivate.DoesNotExist:
            return None

@shared_task
def upload_pdf(data):
    filename = data["trackinginfo_number"] + '.pdf'
    pdf_file = get_object(filename)
    content = data["labeldata_content"]

    if not pdf_file:
        r = requests.get(content,  headers={"APIToken": settings.TEAPPLIX_API_TOKEN}, allow_redirects=True)
        pdf_file = UploadPrivate(user=request.user)
        pdf_file.file.save(filename, ContentFile(r.content))
        pdf_file.save()

def save_tracking(json_format, label_id):

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
        upload_pdf.delay(data)
        savedtracking_serializer.save()


def save_response_status(label_status, status, response):
    label_status.create_status = status
    label_status.response_data = response
    label_status.save()


@shared_task
def create_labels(payload, uuid_gen):
    try:
        label_status = LabelStatus(label_unique_id=uuid_gen)
        label_status.save()
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
            save_tracking(response, payload['label_unique_id'])
            save_response_status(label_status, LabelStatus.Statuses.CREATED, response)
            return True, response
        else:
            save_response_status(label_status, LabelStatus.Statuses.FAILED, response)
            return False, response

    except Exception as e:
        save_response_status(label_status, LabelStatus.Statuses.FAILED, str(e))
        return False, str(e)



