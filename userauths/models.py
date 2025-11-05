from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=8000)

    def __str__(self):
        return self.username