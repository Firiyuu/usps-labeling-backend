from rest_framework import serializers
from .models import (
    Labels,
    Packages,
    LabelsPrinted,
    ShippingRates,
    AddressBook,
    AddressValidation,
    SquareCustomerInfo,
    SquareCard,
    PrepayAccount,
    PrepayHistory,
    SellerAccounts,
    Orders,
    Items,
    Customs,
)
from drf_writable_nested.serializers import WritableNestedModelSerializer


class ZoneSerializer(serializers.Serializer):
    to_zip = serializers.CharField(max_length=200)
    from_zip = serializers.CharField(max_length=200)


class SellerCreateSerializer(serializers.Serializer):
    account_id = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200)


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = (
            'pk',
            'order',
            'name',
            'quantity',
            'price',
            'weight',
            'dimensions_length',
            'dimensions_width',
            'dimensions_depth',
            'dimensions_unit',
            'identical_package',
            'method'
        )


class CustomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customs
        fields = (
            'pk',
            'order',
            'customs_name',
            'customs_sku',
            'customs_description',
            'customs_quantity',
            'customs_amount',
            'customs_currency',
            'customs_country',
            'tariff_code'
        )


class OrderCreateSerializer(WritableNestedModelSerializer):
    is_archived = serializers.BooleanField(default=False, required=False)
    custom_items = CustomsSerializer(many=True)
    line_items = ItemSerializer(many=True)

    class Meta:
        model = Orders
        fields = (
            'pk',
            'user',
            'line_items',
            'custom_items',
            'order_number',
            'name',
            'weight_unit',
            'company',
            'address1',
            'address2',
            'city',
            'state',
            'zipcode',
            'country',
            'phone',
            'email',
            'is_archived'
        )


class SellerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerAccounts
        fields = (
            'user',
            'vsaccount_id',
            'account_id',
            'password'

        )


class LabelsPrintedSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabelsPrinted
        fields = (
            'user',
            'label_id',
            'clientrequest_id',
            'trackinginfo_number',
            'trackinginfo_carriername',
            'labeldata_type',
            'labeldata_content',
            'success',
            'code',
            'message',
            'provider'
        )


class ShippingRatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingRates
        fields = (
            'carrier_name',
            'unit',
            'value',
            'zone'
        )


class AddressValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressValidation
        fields = (
            'pk',
            'address_street',
            'address_city',
            'address_state',
            'address_zip'
         )


class PackagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Packages
        fields = (
            'pk',
            'order',
            'weight_value',
            'weight_unit',
            'dimensions_length',
            'dimensions_width',
            'dimensions_depth',
            'method',
            'imgformat_layout',
            'imgformat_type',
            'imgformat_labelreturn',
            'is_return',
            'provider'
        )


class LabelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labels
        packages = PackagesSerializer(many=True)
        fields = (
            'user',
            'sender_name',
            'sender_company',
            'sender_zip',
            'sender_city',
            'sender_state',
            'sender_phone',
            'sender_email',
            'sender_country',
            'sender_country_code',
            'sender_address1',
            'sender_address2',
            'receiver_name',
            'receiver_company',
            'receiver_email',
            'receiver_zip',
            'receiver_city',
            'receiver_state',
            'receiver_country',
            'receiver_country_code',
            'receiver_phone',
            'receiver_address1',
            'receiver_address2'
        )


class AddressBookSerializer(serializers.ModelSerializer):
    company = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        required=False
    )
    email = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        required=False
    )
    is_archived = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = AddressBook
        fields = (
            'user',
            'pk',
            'name',
            'company',
            'email',
            'zipcode',
            'city',
            'state',
            'phone',
            'country',
            'country_code',
            'address1',
            'is_archived'
        )


class LabelsGeneralSerializer(WritableNestedModelSerializer):

    # Reverse FK relation
    packages = PackagesSerializer(many=True)
    sender_company = serializers.CharField(
        allow_null=True,
        allow_blank=True, 
        required=False
    )
    sender_email = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        required=False
    )
    receiver_company = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        required=False
    )
    receiver_email = serializers.CharField(
        allow_null=True,
        allow_blank=True,
        required=False
    )
    is_archived = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Labels
        fields = (
            'pk',
            'user',
            'label_unique_id',
            'sender_company',
            'sender_name',
            'sender_zip',
            'sender_city',
            'sender_state',
            'sender_phone',
            'sender_email',
            'sender_country',
            'sender_country_code',
            'sender_address1',
            'receiver_name',
            'receiver_company',
            'receiver_email',
            'receiver_zip',
            'receiver_city',
            'receiver_state',
            'receiver_country',
            'receiver_country_code',
            'receiver_phone',
            'receiver_address1',
            'packages',
            'is_archived'
        )


class LabelsGeneralSerializerGet(WritableNestedModelSerializer):

    # Reverse FK relation
    packages = PackagesSerializer(many=True)

    class Meta:
        model = Labels
        fields = (
            'pk',
            'user',
            'label_unique_id',
            'sender_name',
            'sender_company',
            'sender_zip',
            'sender_city',
            'sender_state',
            'sender_phone',
            'sender_email',
            'sender_country',
            'sender_country_code',
            'sender_address1',
            'receiver_name',
            'receiver_company',
            'receiver_zip',
            'receiver_city',
            'receiver_state',
            'receiver_country',
            'receiver_country_code',
            'receiver_phone',
            'receiver_email',
            'receiver_address1',
            'timestamp',
            'packages',
        )


class SquareCustomerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SquareCustomerInfo
        fields = (
            'pk',
            'user',
            'customer_id',
            'created_at',
            'updated_at',
        )


class SquareCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SquareCard
        fields = (
            'pk',
            'customer',
            'card_id',
            'created_at',
            'updated_at',
        )


class PrepayAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrepayAccount
        fields = (
            'pk',
            'user',
            'balance',
            'created_at',
            'updated_at',
        )


class PrepayHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrepayHistory
        fields = (
            'pk',
            'user',
            'detail',
            'amount',
            'prev_balance',
            'new_balance',
            'payment_method',
            'payment_id',
            'idempotency_key',
            'source_id',
            'created_at',
            'updated_at',
        )
