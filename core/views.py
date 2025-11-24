from decimal import Decimal
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from core.models import Category, Tags, Vendor, Product, ProductImages, CartOrder, CartOrderItems, ProductReview, Wishlist, Address, PTCCurrency
from django.db.models import Q
from django.http import JsonResponse, HttpResponseNotAllowed
from django.db.models import Sum
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from core.utils import spend_ptc_bucks
from useradmin.decorators import custom_admin_required

def base(request):
    return render(request, 'core/base.html',)

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Must be logged in to view Profile.")
        return redirect('userauths:login')
    else:
        return render(request, 'core/buyer_dashboard.html',)

def seller(request):
    return render(request, 'useradmin/dashboard.html',)

def home(request):
    # Only show active products, newest first
    products = Product.objects.filter(status=True).order_by('-date')

    context = {
        'products': products,
    }
    return render(request, 'core/home.html', context)

def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)

    context = {
        'product': product,
    }

    return render(request, 'core/product_detail.html', context)

def search_view(request):
    query = request.GET.get('q')
    products = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query), status=True).order_by('-date')

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'core/search.html', context)

def add_to_cart_view(request, pid):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    product = get_object_or_404(Product, pid=pid)
    qty = int(request.POST.get('qty', 1)) if request.POST.get('qty') else 1

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Login required.'})

    order, _ = CartOrder.objects.get_or_create(user=request.user, paid_status=False)

    item, created = CartOrderItems.objects.get_or_create(
        order=order,
        item=product.title,
        defaults={
            'invoice_no': f'INV{order.id}{product.pid}',
            'image': product.image.url if product.image else '',
            'price': product.price,
            'qty': qty,
            'total': product.price * qty,
            'product_status': 'processing',
        }
    )

    if not created:
        item.qty += qty
        item.total = item.price * item.qty
        item.save()

    total_qty = CartOrderItems.objects.filter(order=order).aggregate(total_qty=Sum('qty'))['total_qty'] or 0
    return JsonResponse({'success': True, 'product_name': product.title, 'new_cart_count': total_qty})


def cart_view(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Must be logged in to view cart.")
        return redirect('userauths:login')

    order, _ = CartOrder.objects.get_or_create(user=request.user, paid_status=False)
    items = CartOrderItems.objects.filter(order=order)
    total_price = sum(i.total for i in items)

    context = {'items': items, 'total_price': total_price}
    return render(request, 'core/cart.html', context)


def update_cart_view(request, item_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        item = CartOrderItems.objects.get(id=item_id)
    except CartOrderItems.DoesNotExist:
        return JsonResponse({"success": False, "error": "Item not found"})

    try:
        data = json.loads(request.body)
        action = data.get("action")
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"})

    if action == "increase":
        item.qty += 1
        item.total = item.price * item.qty
        item.save()

    elif action == "decrease":
        item.qty -= 1
        if item.qty > 0:
            item.total = item.price * item.qty
            item.save()
        else:
            item.delete()

    elif action == "remove":
        item.delete()
    else:
        return JsonResponse({"success": False, "error": "Invalid action"})

    order = item.order if item.id else CartOrder.objects.get(id=item.order.id)
    cart_items = CartOrderItems.objects.filter(order=order)
    cart_total = sum(i.total for i in cart_items)

    return JsonResponse({
        "success": True,
        "qty": item.qty if action != "remove" and item.id else 0,
        "item_total": item.total if action != "remove" and item.id else 0,
        "cart_total": cart_total,
        "removed": action == "remove" or item.qty <= 0
    })

def checkout_view(request):
    wallet, _ = PTCCurrency.objects.get_or_create(user=request.user)
    order, _ = CartOrder.objects.get_or_create(user=request.user, paid_status=False)
    items = CartOrderItems.objects.filter(order=order)
    total_price = sum(i.total for i in items)

    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect('core:cart')

    if request.method == "POST":
        # Collect form data
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        address_text = request.POST.get("address")
        city = request.POST.get("city")
        postcode = request.POST.get("postcode")
        country = request.POST.get("country")
        payment_method = request.POST.get("payment_method")

        if not all([full_name, email, address_text, city, postcode, country, payment_method]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('core:checkout')

        # Save or update the user's address
        address, _ = Address.objects.get_or_create(user=request.user)
        address.full_name = full_name
        address.email = email
        address.address = address_text
        address.city = city
        address.postcode = postcode
        address.country = country
        address.save()

        # PTC Bucks payment
        if payment_method == "ptc_bucks":
            buyer_wallet = PTCCurrency.objects.get(user=request.user)

            if buyer_wallet.balance >= total_price:
                # Deduct from buyer
                spend_ptc_bucks(request.user, total_price, description="Checkout payment")

                # Mark order as paid
                order.paid_status = True
                order.payment_method = "PTC Bucks"
                order.save()

                # Transfer funds to sellers
                for item in items:
                    try:
                        product = Product.objects.get(title=item.item)
                        seller = product.user
                        seller_wallet, _ = PTCCurrency.objects.get_or_create(user=seller)
                        seller_wallet.balance += item.total
                        seller_wallet.save()

                        from core.models import PTCCurrencyTransaction
                        PTCCurrencyTransaction.objects.create(
                            user=seller,
                            amount=item.total,
                            transaction_type="credit",
                            description=f"Sale of {product.title} to {request.user.username}",
                        )
                    except Product.DoesNotExist:
                        continue

                messages.success(
                    request,
                    f"Your order has been placed using PTC Bucks! Remaining balance: {buyer_wallet.balance - total_price}",
                )
                return redirect('core:home')
            else:
                messages.error(request, "Insufficient PTC Bucks balance.")
                return redirect('core:checkout')

    context = {
        "items": items,
        "total_price": total_price,
        "wallet_balance": wallet.balance,
    }
    return render(request, "core/checkout.html", context)

def place_order_view(request):
    if request.method == "POST":
        user = request.user
        order = CartOrder.objects.filter(user=user, paid_status=False).first()
        if not order or not order.items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("core:cart")

        # You can capture billing info here
        email = request.POST.get("email")
        address = request.POST.get("address")
        
        order.email = email
        order.address = address
        order.paid_status = True  # mark as paid / processed
        order.save()

        messages.success(request, "Order placed successfully!")
        return redirect("core:home")
    return redirect("core:checkout")

def update_info(request):
    pass

def my_orders_view(request):
    """
    Displays all past orders the user has made.
    TODO: Filter paid orders, show products, quantities, total spent, and order status.
    """
    orders = CartOrder.objects.filter(user=request.user, paid_status=True).order_by('-order_date')
    context = {
        "orders": orders,
    }
    return render(request, "core/my_orders.html", context)