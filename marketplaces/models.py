from django.contrib.auth.models import User
from django.db import models


class Marketplaces(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    marketplace = models.CharField(max_length=100)
    unique_id = models.CharField(max_length=100)
    data = models.JSONField(null=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
