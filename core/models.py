from django.db import models
from core.storage_backends import PublicMediaStorage, PrivateMediaStorage


class Items(models.Model):
    order = models.IntegerField()
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    weight = models.CharField(max_length=100)
    dimensions_length = models.CharField(max_length=100)
    dimensions_width = models.CharField(max_length=100)
    dimensions_depth = models.CharField(max_length=100)
    dimensions_unit = models.CharField(max_length=100)
    identical_package = models.IntegerField()
    method = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'core_items'
        ordering = ['order']

    def __str__(self):
        return self.name


class Customs(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    order = models.IntegerField()
    customs_name = models.CharField(max_length=100)
    customs_sku = models.CharField(max_length=100)
    customs_description = models.CharField(max_length=100)
    customs_quantity = models.CharField(max_length=100)
    customs_amount = models.CharField(max_length=100)
    customs_currency = models.CharField(max_length=100)
    customs_country = models.CharField(max_length=100)
    tariff_code = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'core_customs'
        ordering = ['order']

    def __str__(self):
        return self.customs_name


class Orders(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    line_items = models.ManyToManyField(Items)
    custom_items = models.ManyToManyField(Customs)
    order_number = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    weight_unit = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    is_archived = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'core_orders'

    def __str__(self):
        return self.line_items


class Packages(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    order = models.IntegerField()
    weight_value = models.CharField(max_length=100)
    weight_unit = models.CharField(max_length=100)
    dimensions_length = models.CharField(max_length=100)
    dimensions_width = models.CharField(max_length=100)
    dimensions_depth = models.CharField(max_length=100)
    dimensions_unit = models.CharField(max_length=100)
    reference = models.CharField(max_length=100)
    method = models.CharField(max_length=100)
    imgformat_layout = models.CharField(max_length=100)
    imgformat_type = models.CharField(max_length=100)
    imgformat_labelreturn = models.CharField(max_length=100)
    is_return = models.BooleanField()
    provider = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'core_packages'
        ordering = ['order']

    def __str__(self):
        return self.reference


class Labels(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    packages = models.ManyToManyField(Packages)
    label_unique_id = models.CharField(max_length=100)
    sender_name = models.CharField(max_length=100)
    sender_company = models.CharField(max_length=100)
    sender_zip = models.CharField(max_length=100)
    sender_city = models.CharField(max_length=100)
    sender_state = models.CharField(max_length=100)
    sender_phone = models.CharField(max_length=100)
    sender_email = models.CharField(max_length=100)
    sender_country = models.CharField(max_length=100)
    sender_country_code = models.CharField(max_length=100)
    sender_address1 = models.CharField(max_length=100)
    sender_address2 = models.CharField(max_length=100)
    sender_address3 = models.CharField(max_length=100)
    receiver_name = models.CharField(max_length=100)
    receiver_company = models.CharField(max_length=100)
    receiver_zip = models.CharField(max_length=100)
    receiver_city = models.CharField(max_length=100)
    receiver_state = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=100)
    receiver_email = models.CharField(max_length=100)
    receiver_country = models.CharField(max_length=100)
    receiver_country_code = models.CharField(max_length=100)
    receiver_address1 = models.CharField(max_length=100)
    receiver_address2 = models.CharField(max_length=100)
    receiver_address3 = models.CharField(max_length=100)
    is_archived = models.BooleanField(default=False)
    is_international = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'core_labels'

class LabelStatus(models.Model):
    class Statuses(models.TextChoices):
        PROCESSING = 'Processing'
        FAILED = 'Failed'
        CREATED = 'Created'
    label_unique_id = models.CharField(max_length=100)
    create_status = models.CharField(max_length=100, choices=Statuses.choices, default=Statuses.PROCESSING)
    response_data = models.JSONField(null=True)


class LabelsPrinted(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    label_id = models.CharField(max_length=100)
    clientrequest_id = models.CharField(max_length=100)
    trackinginfo_number = models.CharField(max_length=100)
    trackinginfo_carriername = models.CharField(max_length=100)
    labeldata_type = models.CharField(max_length=100)
    labeldata_content = models.CharField(max_length=100)
    success = models.BooleanField()
    code = models.IntegerField()
    message = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'core_labels_printed'


class ShippingRates(models.Model):
    carrier_name = models.CharField(max_length=100)
    unit = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    zone = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)


class AddressValidation(models.Model):
    address_street = models.CharField(max_length=100)
    address_street2 = models.CharField(max_length=100)
    address_city = models.CharField(max_length=100)
    address_zip = models.CharField(max_length=100)
    address_country = models.CharField(max_length=100)
    address_country_code = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    address_state = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'core_address_validate'


class AddressBook(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=100)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    address3 = models.CharField(max_length=100)
    is_archived = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'core_addressbook'


class SquareCustomerInfo(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    customer_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_square_customer'


class SquareCard(models.Model):
    customer = models.ForeignKey(SquareCustomerInfo, on_delete=models.CASCADE)
    card_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_square_card'


class PrepayAccount(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    balance = models.DecimalField(decimal_places=2, max_digits=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_prepay_account'


class PrepayHistory(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    detail = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=100)
    prev_balance = models.DecimalField(decimal_places=2, max_digits=100)
    new_balance = models.DecimalField(decimal_places=2, max_digits=100)
    payment_method = models.CharField(max_length=100, blank=True)
    idempotency_key = models.CharField(max_length=100, blank=True)
    payment_id = models.CharField(max_length=100, blank=True)
    source_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_prepay_history'


class SellerAccounts(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    vsaccount_id = models.CharField(max_length=100)
    account_id = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_seller_account'


class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=PublicMediaStorage())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UploadPrivate(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=PrivateMediaStorage())
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='uploads',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
