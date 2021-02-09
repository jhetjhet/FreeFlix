from django.db import models
from django.contrib.auth.models import AbstractUser

from uuid import uuid4

class Flixer(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    email = models.EmailField(null=False, blank=False)

    def __str__(self):
        return self.username