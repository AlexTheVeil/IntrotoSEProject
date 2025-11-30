# core/utils.py

from decimal import Decimal
from core.models import PTCCurrency, PTCCurrencyTransaction
from useradmin.decorators import custom_admin_required
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging
from core.models import CartOrderItems

logger = logging.getLogger(__name__)


def notify_vendors_of_order(order):
    """Send an email notification to each vendor who has items in the order.
    Uses CartOrderItems.product FK to reliably determine vendor ownership.
    """
    # Group cart items by vendor
    items = CartOrderItems.objects.filter(order=order).select_related('product__user')
    vendor_map = {}
    for ci in items:
        vendor = ci.product.user if ci.product else None
        if not vendor:
            continue
        vendor_map.setdefault(vendor, []).append(ci)

    for vendor, v_items in vendor_map.items():
        if not vendor.email:
            logger.info("Skipping vendor %s (id=%s): no email address configured", getattr(vendor, 'username', None), getattr(vendor, 'id', None))
            continue

        subject = f"New order #{order.id} contains your products"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or 'noreply@example.com'
        to_email = [vendor.email]

        # Build plain text body
        lines = [f"Order #{order.id}", f"Buyer: {order.user.username if order.user else 'Guest'}", ""]
        total = 0
        for ci in v_items:
            lines.append(f"{ci.product.title if ci.product else ci.item} — qty {ci.qty} — ${ci.total}")
            total += float(ci.total)
        lines.append("")
        lines.append(f"Total for your items: ${total}")

        text_body = "\n".join(lines)

        # HTML body (simple)
        html_body = render_to_string('emails/vendor_new_order.html', {'order': order, 'vendor': vendor, 'items': v_items, 'vendor_total': total})

        msg = EmailMultiAlternatives(subject, text_body, from_email, to_email)
        msg.attach_alternative(html_body, "text/html")
        try:
            msg.send()
            logger.info("Sent vendor notification to %s for order %s", vendor.email, order.id)
        except Exception as exc:
            logger.exception("Failed sending vendor notification to %s for order %s: %s", vendor.email, order.id, exc)

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
