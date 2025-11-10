from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from userauths.models import User
from core.models import PTCCurrency

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_currency(sender, instance, created, **kwargs):
    if created:
        PTCCurrency.objects.create(user=instance, balance=100.0)  # Give 100 starting bucks