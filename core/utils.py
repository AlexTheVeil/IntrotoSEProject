# core/utils.py

from decimal import Decimal
from core.models import PTCCurrency, PTCCurrencyTransaction
from useradmin.decorators import custom_admin_required

def spend_ptc_bucks(user, amount, description="Purchase"):
    amount = Decimal(amount)
    wallet = PTCCurrency.objects.get(user=user)

    if wallet.balance < amount:
        return False  # Not enough funds

    wallet.balance -= amount
    wallet.save()

    PTCCurrencyTransaction.objects.create(
        user=user,
        amount=amount,
        transaction_type='debit',
        description=description
    )
    return True

def add_ptc_bucks(user, amount, description="Credit"):
    amount = Decimal(amount)
    wallet = PTCCurrency.objects.get(user=user)
    wallet.balance += amount
    wallet.save()

    PTCCurrencyTransaction.objects.create(
        user=user,
        amount=amount,
        transaction_type='credit',
        description=description
    )
