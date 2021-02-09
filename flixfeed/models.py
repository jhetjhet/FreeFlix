from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from uuid import uuid4

class Rate (models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=False, on_delete=models.SET_NULL, related_name='rated')
    score = models.IntegerField(
        null=False,
        blank=False,
        validators=(
            MaxValueValidator(10),
            MinValueValidator(1),
        )
    )
    date_rated = models.DateTimeField(auto_now_add=True)