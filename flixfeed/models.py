from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

class Rate (models.Model):
    user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rated')
    score = models.IntegerField(
        null=False,
        blank=False,
        validators=(
            MaxValueValidator(10),
            MinValueValidator(1),
        )
    )
    date_rated = models.DateTimeField(auto_now_add=True)
