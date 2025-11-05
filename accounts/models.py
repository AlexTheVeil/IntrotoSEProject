# accounts/models.py
from django.db import models
from django.conf import settings  # <- this gives you access to AUTH_USER_MODEL

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"
