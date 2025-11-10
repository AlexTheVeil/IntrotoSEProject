from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from core.models import Category, Tags, Vendor, Product, ProductImages, CartOrder, CartOrderItems, ProductReview, Wishlist, Address
from django.db.models import Q
from django.http import JsonResponse, HttpResponseNotAllowed
from django.db.models import Sum

def base(request):
    return render(request, 'core/base.html',)

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
    # Only allow POST requests
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # Get product safely
    product = get_object_or_404(Product, pid=pid)

    # Get quantity from POST data, default to 1
    try:
        qty = int(request.POST.get('qty', 1))
        if qty < 1:
            qty = 1
    except ValueError:
        qty = 1

    # Ensure user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'You must be logged in to add items to cart.'})

    # Get or create the current unpaid cart for the user
    order, _ = CartOrder.objects.get_or_create(user=request.user, paid_status=False)

    # Get or create the item in the cart
    item, created = CartOrderItems.objects.get_or_create(
        order=order,
        item=product.title,  # Use product title for CartOrderItems.item
        defaults={
            'invoice_no': f'INV{order.id}{product.pid}',
            'image': product.image.url if product.image else '',
            'price': product.price,
            'qty': qty,
            'total': product.price * qty,
            'product_status': 'processing',
        }
    )

    # If item already exists, update quantity and total
    if not created:
        item.qty += qty
        item.total = item.price * item.qty
        item.save()

    # Calculate total quantity in cart
    total_qty = CartOrderItems.objects.filter(order=order).aggregate(total_qty=Sum('qty'))['total_qty'] or 0

    return JsonResponse({'success': True, 'product_name': product.title, 'new_cart_count': total_qty})

def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Or wherever you want unauthenticated users to go
    
    order, created = CartOrder.objects.get_or_create(user=request.user, paid_status=False)
    items = CartOrderItems.objects.filter(order=order)
    
    total_price = sum(item.total for item in items)
    
    context = {
        'items': items,
        'total_price': total_price
    }
    return render(request, 'core/cart.html', context)