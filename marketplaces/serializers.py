from rest_framework import serializers
from .models import (
    Marketplaces
)

from drf_writable_nested.serializers import WritableNestedModelSerializer


class MarketplacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketplaces
        fields = (
            'id',
            'user',
            'marketplace',
            'unique_id',
            'data',
            'created_at',
            'updated_at'
        )


class MarketplaceSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Marketplaces
        fields = (
            'id',
            'user',
            'marketplace',
            'unique_id',
            'data',
            'created_at',
            'updated_at'
        )
