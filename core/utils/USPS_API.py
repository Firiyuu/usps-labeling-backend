import requests
import xmltodict, json
import base64
from core.models import (
    LabelsPrinted,
    Upload
)
from core.serializers import (
    LabelsPrintedSerializer
)
import base64
from django.core.files.base import ContentFile

class USPSAPI(object):
    def __init__(self):
        self.headers = headers = {
            'Content-Type': 'text/xml; charset=utf-8;',
        }
        self.api_url = "https://gss.usps.com/usps-cpas/GSSAPI/GSSMailerWebservice.asmx"

    def __str__(self):
        return self.token

    def _parse_response(self, response):
        xml_resp = xmltodict.parse(response.content.decode("utf-8"))

        json_resp = json.dumps(xml_resp)
        return json.loads(json_resp)


    def authenticate(self):
        payload = """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
        <AuthenticateUser xmlns="https://gss.usps.com/usps-cpas/GSSAPI/">
        <UserID>UWL_SHIPENGINE_API</UserID>
        <Password>djMjnq9FtBUk</Password>
        <LocationID>HILLBURNUNITEDWLDUSM</LocationID>
        <WorkstationID>UWL_API</WorkstationID>
        </AuthenticateUser>
        </soap:Body>
        </soap:Envelope>"""

        response = requests.request("POST", self.api_url, headers=self.headers, data = payload)
        json_resp = self._parse_response(response)
        return json_resp["soap:Envelope"]["soap:Body"]["AuthenticateUserResponse"]['AuthenticateUserResult']

    def logout(self, access_token):
        xml_doc = F"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <LogoutUser xmlns="https://gss.usps.com/usps-cpas/GSSAPI/">
                <AccessToken>{access_token}</AccessToken>
                </LogoutUser>
            </soap:Body>
            </soap:Envelope>"""
        response = self.post(xml_doc)

        return response["soap:Envelope"]["soap:Body"]

    def post(self, data):
        response = requests.request("POST", self.api_url, headers=self.headers, data = data)
        json_resp = self._parse_response(response)

        return json_resp

    def cancel_label(self, payload):
        access_token = self.authenticate()
        xml_doc = F"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <RemovePackageFromOpenDispatch xmlns="https://gss.usps.com/usps-cpas/GSSAPI/">
                <PackageID>{payload['label_unique_id']}</PackageID>
                <MailingAgentID>UNITEDWLDUSM</MailingAgentID>
                <BoxNumber>1</BoxNumber>
                <AccessToken>{access_token['AccessToken']}</AccessToken>
                </RemovePackageFromOpenDispatch>
            </soap:Body>
            </soap:Envelope>"""
        response = self.post(xml_doc)
        self.logout(access_token['AccessToken'])

        return response["soap:Envelope"]["soap:Body"]

    def get_rates(self, payload):
        access_token = self.authenticate()
        xml_doc = F"""<?xml version="1.0" encoding="UTF-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
           <soap:Body>
              <CalculatePostage xmlns="https://gss.usps.com/usps-cpas/GSSAPI/">
                 <xmlDoc>
                    <CalculatePostage>
                       <CountryCode>{payload['country_code']}</CountryCode>
                       <PostalCode>{payload['postal_code']}</PostalCode>
                       <ServiceType>{payload['service_type']}</ServiceType>
                       <RateType>{payload['rate_type']}</RateType>
                       <PackageWeight>{payload['package_weight']}</PackageWeight>
                       <UnitOfWeight>{payload['unite_weight']}</UnitOfWeight>
                       <PackageLength>{payload['package_length']}</PackageLength>
                       <PackageWidth>{payload['package_weight']}</PackageWidth>
                       <PackageHeight>{payload['package_height']}</PackageHeight>
                       <UnitOfMeasurement>{payload['unit_measurement']}</UnitOfMeasurement>
                       <NonRectangular>0</NonRectangular>
                       <DestinationLocationID />
                       <RateAdjustmentCode>NORMAL RATE</RateAdjustmentCode>
                       <ExtraServiceCode />
                       <EntryFacilityZip />
                       <CustomerReferenceID />
                    </CalculatePostage>
                 </xmlDoc>
                 <AccessToken>{access_token['AccessToken']}</AccessToken>
              </CalculatePostage>
           </soap:Body>
        </soap:Envelope>"""

        response = self.post(xml_doc)
        return response["soap:Envelope"]["soap:Body"]

    def print_labels(self, labels_processed, access_token, file_format, user, label_unique_id):
        printed_labels = []
        for label in labels_processed:
            xml_doc = F"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <GetImageLabelsForPackage xmlns="https://gss.usps.com/usps-cpas/GSSAPI/">
                <PackageID>{label}</PackageID>
                <MailingAgentID>UNITEDWLDUSM</MailingAgentID>
                <BoxNumber>1</BoxNumber>
                <FileFormat>{file_format}</FileFormat>
                <AccessToken>{access_token['AccessToken']}</AccessToken>
                </GetImageLabelsForPackage>
            </soap:Body>
            </soap:Envelope>"""

            response = self.post(xml_doc)
            label_base64 = response["soap:Envelope"]["soap:Body"]
            label_message = label_base64['GetImageLabelsForPackageResponse']['GetImageLabelsForPackageResult']

            labal_data = self.save_tracking(label, label_message, user, label_unique_id)
            printed_labels.append(labal_data)

        return printed_labels

    def save_tracking(self, label_id, label_message, user, label_unique_id):
        label_content = label_message['Label']['base64Binary']

        filename = F'{label_id}.pdf'
        pdf_file = Upload()
        pdf_file.file.save(filename, ContentFile(base64.b64decode(label_content)))
        pdf_file.save()

        data = {
            'label_id': label_unique_id,
            'clientrequest_id': str(label_id),
            'trackinginfo_number': str(label_id),
            'trackinginfo_carriername':  'USPS',
            'labeldata_type':  'pdf',
            'labeldata_content': pdf_file.file.url,
            'success': True if label_message['Message'] == 'Success' else False,
            'code':  label_message['ResponseCode'],
            'message':  label_message['Message'],
            'provider':  'GSS',
            'user': user.id
        }

        savedtracking_serializer = LabelsPrintedSerializer(data=data)
        if savedtracking_serializer.is_valid():
            savedtracking_serializer.save()
            return savedtracking_serializer.data
        return savedtracking_serializer.errors

    def domestic_package(self, payload, labels_processed, access_token, user):
        payload_packages = payload['packages']
        for i in range(0, len(payload["packages"])):
            package_ = payload['label_unique_id'].replace("-", "")[:20]
            package_id = str(package_) + str(i)
            xml_doc = F"""<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <LoadAndProcessPackageData xmlns="https://gss.usps.com/usps-cpas/GSSAPI/">
                    <xmlDoc>
                    <Manifest>
                    <Dispatch
                        xmlns="mailerdataformatf07.xsd">
                        <ShippingAgentID>UNITEDWLDUSM</ShippingAgentID>
                        <ReceivingAgentID>USPSERVICUSD</ReceivingAgentID>
                        <DispatchID></DispatchID>
                        <DispatchDateTime>2020-10-22T11:42:46</DispatchDateTime>
                        <TimeZone>EST</TimeZone>
                        <FileFormatVersion>6</FileFormatVersion>
                    </Dispatch>
                        <Package PackageID="{package_id}" >
                        xmlns="mailerdataformatf07.xsd">
                        <OrderID>{package_id}</OrderID>
                        <ItemValueCurrencyType>USD</ItemValueCurrencyType>
                        <SenderName>{payload['sender_name']}</SenderName>
                        <SenderFirstName>{payload['sender_name']}</SenderFirstName>
                        <SenderMiddleInitial></SenderMiddleInitial>
                        <SenderLastName></SenderLastName>
                        <SenderBusinessName>{payload['sender_company']}</SenderBusinessName>
                        <SenderAddress_Line_1>{payload['sender_address1']}</SenderAddress_Line_1>
                        <SenderAddress_Line_2>{payload['sender_address2']}</SenderAddress_Line_2>
                        <SenderAddress_IsPOBox>N</SenderAddress_IsPOBox>
                        <SenderCity>{payload['sender_city']}</SenderCity>
                        <SenderProvince>{payload['sender_state']}</SenderProvince>
                        <SenderPostal_Code>{payload['sender_zip']}</SenderPostal_Code>
                        <SenderCountry_Code>{payload['sender_country_code']}</SenderCountry_Code>
                        <SenderPhone>{payload['sender_phone']}</SenderPhone>
                        <SenderEmail>{payload['sender_email']}</SenderEmail>
                        <RecipientName>{payload['receiver_name']}</RecipientName>
                        <RecipientFirstName>{payload['receiver_name']}</RecipientFirstName>
                        <RecipientMiddleInitial></RecipientMiddleInitial>
                        <RecipientLastName></RecipientLastName>
                        <RecipientBusinessName>{payload['receiver_company']}</RecipientBusinessName>
                        <RecipientAddress_Line_1>{payload['receiver_address1']}</RecipientAddress_Line_1>
                        <RecipientAddress_Line_2>{payload['receiver_address2']}</RecipientAddress_Line_2>
                        <RecipientAddress_Line_3></RecipientAddress_Line_3>
                        <RecipientInLineTranslationAddressLine1></RecipientInLineTranslationAddressLine1>
                        <RecipientInLineTranslationAddressLine2></RecipientInLineTranslationAddressLine2>
                        <RecipientAddress_IsPOBox>N</RecipientAddress_IsPOBox>
                        <RecipientCity>{payload['receiver_city']}</RecipientCity>
                        <RecipientProvince>{payload['receiver_state']}</RecipientProvince>
                        <RecipientPostal_Code>{payload['receiver_zip']}</RecipientPostal_Code>
                        <RecipientCountry_Code>{payload['receiver_country_code']}</RecipientCountry_Code>
                        <RecipientPhone></RecipientPhone>
                        <RecipientEmail></RecipientEmail>
                        <PackageType>M</PackageType>
                        <PackageShape>Custom Box</PackageShape>
                        <TaxpayerID></TaxpayerID>
                        <ShippingandHandling></ShippingandHandling>
                        <ShippingCurrencyType>USD</ShippingCurrencyType>
                        <PackageID>{package_id}</PackageID>
                        <PackageWeight>{0.8}</PackageWeight>
                        <WeightUnit>{payload_packages[i]['weight_unit']}</WeightUnit>
                        <PackageLength>{payload_packages[i]['dimensions_length']}</PackageLength>
                        <PackageWidth>{payload_packages[i]['dimensions_width']}</PackageWidth>
                        <PackageHeight>{payload_packages[i]['dimensions_depth']}</PackageHeight>
                        <UnitOfMeasurement>{payload_packages[i]['dimensions_unit']}</UnitOfMeasurement>

                        <ServiceType>MLO</ServiceType>
                        <RateType>FC</RateType>

                        <PackagePhysicalCount>1</PackagePhysicalCount>
                        <PostagePaid></PostagePaid>
                        <PostagePaidCurrencyType></PostagePaidCurrencyType>
                        <RestrictionType>1</RestrictionType>
                        <RestrictionComments>Quarantine comments
                        </RestrictionComments>
                        <MailingAgentID>UNITEDWLDUSM</MailingAgentID>
                        <ReturnAgentID></ReturnAgentID>
                        <ValueLoaded>N</ValueLoaded>
                        <LicenseNumber></LicenseNumber>
                        <CertificateNumber></CertificateNumber>
                        <InvoiceNumber></InvoiceNumber>
                        <PaymentAndDeliveryTerms></PaymentAndDeliveryTerms>
                        <PFCorEEL>NOEEI 30.37(a)</PFCorEEL>
                        <ReturnServiceRequested>Y</ReturnServiceRequested>
                        <EntryFacilityZip>11219</EntryFacilityZip>
                        <CustomerReferenceID></CustomerReferenceID>
                        <RedirectBusinessName>{payload['sender_company']}</RedirectBusinessName>
                        <RedirectFirstName>John</RedirectFirstName>
                        <RedirectLastName>Underwood</RedirectLastName>
                        <RedirectAddress_Line_1>{payload['sender_address1']}
                        </RedirectAddress_Line_1>
                        <RedirectAddress_Line_2>{payload['sender_address2']}
                        </RedirectAddress_Line_2>
                        <RedirectAddress_Line_3></RedirectAddress_Line_3>
                        <RedirectCity>{payload['sender_city']}</RedirectCity>
                        <RedirectProvince>{payload['sender_state']}</RedirectProvince>

                        <RedirectPostal_Code>{payload['sender_zip']}</RedirectPostal_Code>
                        <RedirectCountry_Code>US</RedirectCountry_Code>
                        <RedirectPhone>{payload['sender_phone']}</RedirectPhone>
                        <RedirectEmail>{payload['sender_email']}</RedirectEmail>
                        <ExporterReferenceType>1</ExporterReferenceType>
                        <ExporterReferenceValue></ExporterReferenceValue>
                        <ExporterPhoneNo></ExporterPhoneNo>
                        <ExporterEmail></ExporterEmail>
                        <ImporterReferenceType></ImporterReferenceType>
                        <ImporterReferenceValue></ImporterReferenceValue>
                        <ImporterPhoneNo></ImporterPhoneNo>
                        <ImporterEmail></ImporterEmail>
                        <DestinationLocationID></DestinationLocationID>
                        <PriceCategoryType></PriceCategoryType>
                        <DestinationEntryType></DestinationEntryType>
                        <RecipientFirstName_Foreign></RecipientFirstName_Foreign>
                        <RecipientLastName_Foreign></RecipientLastName_Foreign>
                        <RecipientBusinessName_Foreign></RecipientBusinessName_Foreign>
                        <RecipientAddress_Line_1_Foreign></RecipientAddress_Line_1_Foreign>
                        <RecipientAddress_Line_2_Foreign></RecipientAddress_Line_2_Foreign>
                        <RecipientAddress_Line_3_Foreign></RecipientAddress_Line_3_Foreign>
                        <RecipientCity_Foreign></RecipientCity_Foreign>
                        <RecipientProvince_Foreign></RecipientProvince_Foreign>
                        <RecipientPostal_Code_Foreign></RecipientPostal_Code_Foreign>
                        <PackageOrderDate></PackageOrderDate>
                        <InsuredAmount></InsuredAmount>

                        </Package>
                    </Manifest>
                    </xmlDoc>
                    <AccessToken>{access_token['AccessToken']}</AccessToken>
                    </LoadAndProcessPackageData>
                </soap:Body>
                </soap:Envelope>"""

            response = self.post(xml_doc)
            response = response["soap:Envelope"]["soap:Body"]['LoadAndProcessPackageDataResponse'][
                'LoadAndProcessPackageDataResult']['Manifest']
            if 'Package_Error' in response:
                return False, response['Package_Error']['Error_Description']

            labels_processed.append(package_id)

        printed_labels = self.print_labels(
            labels_processed,
            access_token,
            payload_packages[0]['imgformat_type'],
            user,
            payload['label_unique_id'],
        )

        data = {
            "labels": printed_labels,
        }
        self.logout(access_token['AccessToken'])

        return True, data

    def international_package(self, payload, labels_processed, access_token, user):
        payload_packages = payload['packages']
        package_count = len(payload["packages"])
        foreign_reciever_name = payload['receiver_name'].split()
        foreign_last_name = foreign_reciever_name[-1]
        foreign_first_name = payload['receiver_name'].rsplit(' ', 1)[0]

        for i in range(0, package_count):
            package_ = payload['label_unique_id'].replace("-", "")[:20]
            package_id = str(package_) + str(i)
            xml_doc = F"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
              <soap:Body>
                <LoadAndProcessPackageData xmlns="https://gss.usps.com/usps-cpas/GSSAPI/">
                  <xmlDoc>
            <Manifest>
                <Dispatch
                    xmlns="mailerdataformatf07.xsd">
                    <ShippingAgentID>UNITEDWLDUSM</ShippingAgentID>
                    <ReceivingAgentID>USPSERVICUSD</ReceivingAgentID>
                    <DispatchID></DispatchID>
                    <DispatchDateTime>2020-10-22T11:42:46</DispatchDateTime>
                    <TimeZone>EST</TimeZone>
                    <FileFormatVersion>6</FileFormatVersion>
                </Dispatch>
            <Package PackageID="{package_id}" xmlns="mailerdataformatf07.xsd">
            <OrderID>{package_id}</OrderID>
            <ItemValueCurrencyType>USD</ItemValueCurrencyType>
            <SenderName>{payload['sender_name']}</SenderName>
            <SenderFirstName>{payload['sender_name']}</SenderFirstName>
            <SenderMiddleInitial></SenderMiddleInitial>
            <SenderLastName></SenderLastName>
            <SenderBusinessName>{payload['sender_company']}</SenderBusinessName>
            <SenderAddress_Line_1>{payload['sender_address1']}</SenderAddress_Line_1>
            <SenderAddress_Line_2>{payload['sender_address2']}</SenderAddress_Line_2>
            <SenderAddress_IsPOBox>N</SenderAddress_IsPOBox>
            <SenderCity>{payload['sender_city']}</SenderCity>
            <SenderProvince>{payload['sender_state']}</SenderProvince>
            <SenderPostal_Code>{payload['sender_zip']}</SenderPostal_Code>
            <SenderCountry_Code>{payload['sender_country_code']}</SenderCountry_Code>
            <SenderPhone>{payload['sender_phone']}</SenderPhone>
            <SenderEmail>{payload['sender_email']}</SenderEmail>
            <RecipientName>{payload['receiver_name']}</RecipientName>
            <RecipientFirstName></RecipientFirstName>
            <RecipientMiddleInitial></RecipientMiddleInitial>
            <RecipientLastName></RecipientLastName>
            <RecipientBusinessName>{payload['receiver_company']}</RecipientBusinessName>
            <RecipientAddress_Line_1>{payload['receiver_address1']}</RecipientAddress_Line_1>
            <RecipientAddress_Line_2>{payload['receiver_address2']}</RecipientAddress_Line_2>
            <RecipientAddress_Line_3></RecipientAddress_Line_3>
            <RecipientInLineTranslationAddressLine1></RecipientInLineTranslationAddressLine1>
            <RecipientInLineTranslationAddressLine2></RecipientInLineTranslationAddressLine2>
            <RecipientAddress_IsPOBox>N</RecipientAddress_IsPOBox>

            <RecipientCity>{payload['receiver_city']}</RecipientCity>
            <RecipientProvince>{payload['receiver_state']}</RecipientProvince>
            <RecipientPostal_Code>{payload['receiver_zip']}</RecipientPostal_Code>
            <RecipientCountry_Code>{payload['receiver_country_code']}</RecipientCountry_Code>

            <RecipientPhone>{payload['receiver_phone']}</RecipientPhone>
            <RecipientEmail>{payload['receiver_email']}</RecipientEmail>
            <PackageType>{payload['package_type']}</PackageType>
            <PackageShape>Custom Box</PackageShape>
            <TaxpayerID></TaxpayerID>
            <ShippingandHandling></ShippingandHandling>
            <ShippingCurrencyType>USD</ShippingCurrencyType>


            <PackageID>{package_id}</PackageID>
            <MailerProvidedUSPSPackageID></MailerProvidedUSPSPackageID>
            <PackageWeight>{0.8}</PackageWeight>
            <WeightUnit>{payload_packages[i]['weight_unit']}</WeightUnit>
            <PackageLength>{payload_packages[i]['dimensions_length']}</PackageLength>
            <PackageWidth>{payload_packages[i]['dimensions_width']}</PackageWidth>
            <PackageHeight>{payload_packages[i]['dimensions_depth']}</PackageHeight>
            <UnitOfMeasurement>{payload_packages[i]['dimensions_unit']}</UnitOfMeasurement>
            <ServiceType>{payload['service_type']}</ServiceType>
            <RateType>{payload['rate_type']}</RateType>
            <PackagePhysicalCount>1</PackagePhysicalCount>
            <PostagePaid></PostagePaid>
            <PostagePaidCurrencyType></PostagePaidCurrencyType>
            <RestrictionType></RestrictionType>
            <RestrictionComments></RestrictionComments>
            <MailingAgentID>UNITEDWLDUSM</MailingAgentID>
            <ReturnAgentID></ReturnAgentID>
            <ValueLoaded>N</ValueLoaded>
            <LicenseNumber></LicenseNumber>
            <CertificateNumber></CertificateNumber>
            <InvoiceNumber></InvoiceNumber>
            <PaymentAndDeliveryTerms></PaymentAndDeliveryTerms>
            <PFCorEEL>NOEEI 30.37(a)</PFCorEEL>
            <ReturnServiceRequested>Y</ReturnServiceRequested>
            <EntryFacilityZip></EntryFacilityZip>
            <CustomerReferenceID></CustomerReferenceID>
            <RedirectBusinessName>{payload['sender_company']}</RedirectBusinessName>
            <RedirectFirstName></RedirectFirstName>
            <RedirectLastName></RedirectLastName>
            <RedirectAddress_Line_1>{payload['sender_address1']}
            </RedirectAddress_Line_1>
            <RedirectAddress_Line_2>{payload['sender_address2']}
            </RedirectAddress_Line_2>
            <RedirectAddress_Line_3></RedirectAddress_Line_3>
            <RedirectCity>{payload['sender_city']}</RedirectCity>
            <RedirectProvince>{payload['sender_state']}</RedirectProvince>
            <RedirectPostal_Code>{payload['sender_zip']}</RedirectPostal_Code>
            <RedirectCountry_Code>US</RedirectCountry_Code>
            <RedirectPhone>{payload['sender_phone']}</RedirectPhone>
            <RedirectEmail>{payload['sender_email']}</RedirectEmail>
            <ExporterReferenceType>{payload['exporter_reference_type']}</ExporterReferenceType>
            <ExporterReferenceValue>{payload['exporter_reference_value']}</ExporterReferenceValue>
            <ExporterPhoneNo>{payload['exporter_phone_number']}</ExporterPhoneNo>
            <ExporterEmail>{payload['exporter_phone_email']}</ExporterEmail>
            <ImporterReferenceType>{payload['importer_reference_type']}</ImporterReferenceType>
            <ImporterReferenceValue>{payload['importer_reference_value']}</ImporterReferenceValue>
            <ImporterPhoneNo>{payload['importer_phone_number']}</ImporterPhoneNo>
            <ImporterEmail>{payload['importer_phone_email']}</ImporterEmail>
            <DestinationLocationID></DestinationLocationID>
            <PriceCategoryType></PriceCategoryType>
            <DestinationEntryType></DestinationEntryType>
            <RecipientFirstName_Foreign>{foreign_first_name}</RecipientFirstName_Foreign>
            <RecipientLastName_Foreign>{foreign_last_name}</RecipientLastName_Foreign>
            <RecipientBusinessName_Foreign>{payload['receiver_company']}</RecipientBusinessName_Foreign>
            <RecipientAddress_Line_1_Foreign>{payload['receiver_address1']}<</RecipientAddress_Line_1_Foreign>
            <RecipientAddress_Line_2_Foreign>{payload['receiver_address2']}</RecipientAddress_Line_2_Foreign>
            <RecipientAddress_Line_3_Foreign></RecipientAddress_Line_3_Foreign>
            <RecipientCity_Foreign>{payload['receiver_city']}</RecipientCity_Foreign>
            <RecipientProvince_Foreign>{payload['receiver_state']}</RecipientProvince_Foreign>
            <RecipientPostal_Code_Foreign>{payload['receiver_zip']}</RecipientPostal_Code_Foreign>
            <PackageOrderDate></PackageOrderDate>
            <InsuredAmount></InsuredAmount>
            <Item xmlns="mailerdataformatf07.xsd">
            <ItemID>{payload['item_id']}</ItemID>
            <CommodityName></CommodityName>
            <ItemDescription>{payload['item_description']}</ItemDescription>
            <CustomsDescription>{payload['item_description']}</CustomsDescription>
            <UnitValue>{payload_packages[i]['weight_value']}</UnitValue>
            <ItemWeight>{payload_packages[i]['weight_unit']}</ItemWeight>
            <UnitOfItemWeight>{payload_packages[i]['weight_unit']}</UnitOfItemWeight>
            <Quantity>1</Quantity>
            <CountryOfOrigin>{payload['sender_country']}</CountryOfOrigin>
            <HTSNumber></HTSNumber>
            <MultiSourceFlag></MultiSourceFlag>
            <OriginalImportCost></OriginalImportCost>
            <ImportCostCurrencyType></ImportCostCurrencyType>
            </Item>
            </Package>
            </Manifest>
            </xmlDoc>
                  <AccessToken>{access_token['AccessToken']}</AccessToken>
                </LoadAndProcessPackageData>
              </soap:Body>
            </soap:Envelope>"""

            response = self.post(xml_doc)
            response = response["soap:Envelope"]["soap:Body"]['LoadAndProcessPackageDataResponse'][
                'LoadAndProcessPackageDataResult']['Manifest']
            if 'Package_Error' in response:
                return False, response['Package_Error']['Error_Description']

            labels_processed.append(package_id)

        printed_labels = self.print_labels(
            labels_processed,
            access_token,
            payload_packages[0]['imgformat_type'],
            user,
            payload['label_unique_id'],
        )

        data = {
            "labels": printed_labels,
        }
        self.logout(access_token['AccessToken'])

        return True, data

    def create_labels(self, payload, user):
        access_token = self.authenticate()
        is_international = payload['is_international']
        labels_processed = list()
        if not is_international:
            self.domestic_package(payload, labels_processed, access_token, user)
        else:
            self.international_package(payload, labels_processed, access_token, user)





