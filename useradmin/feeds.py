from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.core import signing
from django.core.signing import BadSignature
from django.shortcuts import get_object_or_404
from core.models import Product, CartOrder, CartOrderItems
from userauths.models import User


class VendorOrderFeed(Feed):
    """RSS feed for vendor orders. The feed URL includes a signed token
    that confirms the vendor identity. The token is generated in the
    vendor dashboard and presented to the vendor to subscribe with.
    """

    def get_object(self, request, user_id, token):
        try:
            data = signing.loads(token)
        except BadSignature:
            return None

        if data.get('user_id') != user_id:
            return None

        # return the vendor user object
        return get_object_or_404(User, id=user_id)

    def title(self, obj):
        return f"Orders for vendor {obj.username}"

    def link(self, obj):
        # link to vendor dashboard
        return reverse('useradmin:dashboard')

    def description(self, obj):
        return f"Latest orders that include products sold by {obj.username}."

    def items(self, obj):
        # Use the product FK to reliably find cart items belonging to this vendor
        order_ids = (
            CartOrderItems.objects
            .filter(product__user=obj)
            .values_list('order', flat=True)
            .distinct()
        )

        orders = CartOrder.objects.filter(id__in=order_ids).order_by('-order_date')[:25]
        return orders

    def item_title(self, item):
        return f"Order #{item.id} - ${item.price}"

    def item_description(self, item):
        # Show only the items in the order that belong to this vendor
        # List items included in the order
        lines = []
        cart_items = CartOrderItems.objects.filter(order=item).select_related('product')
        for ci in cart_items:
            lines.append(f"{ci.product.title if ci.product else ci.item} — qty {ci.qty} — ${ci.total}")
        buyer = getattr(item, 'user', None)
        buyer_name = buyer.username if buyer else 'Unknown'
        return f"Buyer: {buyer_name}\nItems:\n" + "\n".join(lines)

    def item_link(self, item):
        # Link to the admin order list (vendor may use admin panel link)
        return reverse('useradmin:admin_order_list')
