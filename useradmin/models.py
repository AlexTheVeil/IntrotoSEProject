from django.db import models

class Account(models.Model):
    user_status = models.IntegerField() # 0 = Buyer, 1 = Seller, 2 = Admin
    user_ID = models.IntegerField()
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(default=None)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name