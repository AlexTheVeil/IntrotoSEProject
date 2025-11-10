from core.models import Category, Tags, Vendor, Product, ProductImages, CartOrder, CartOrderItems, ProductReview, Wishlist, Address
from userauths import models
from .models import CartOrder, CartOrderItems
from django.db.models import Sum

def cart_count(request):
    if request.user.is_authenticated:
        order, created = CartOrder.objects.get_or_create(user=request.user, paid_status=False)
        total_qty = CartOrderItems.objects.filter(order=order).aggregate(total_qty=Sum('qty'))['total_qty'] or 0
        return {'cart_count': total_qty}
    return {'cart_count': 0}