from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from .forms import ProductForm
from .models import Product

from rapidfuzz import fuzz, process


# ---------------------------
# Home / Index
# ---------------------------
def index(request):
    return render(request, 'core/index.html')


def home(request):
    """Home page showing product listings (and optional search)."""
    query = request.GET.get('q', '')
    products = Product.objects.all()

    if query:
        products = products.filter(title__icontains=query)

    return render(request, 'core/home.html', {
        'products': products,
        'query': query
    })


# ---------------------------
# Product Creation
# ---------------------------
def add_product(request):
    """Add a new product (admin/staff use)."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if request.user.is_authenticated:
                product.user = request.user
            product.save()
            messages.success(request, f"Product '{product.title}' added successfully!")
            return redirect('add_product')
    else:
        form = ProductForm()

    products = Product.objects.all().order_by('-date')
    return render(request, 'core/add_product.html', {
        'form': form,
        'products': products
    })


# ---------------------------
# Search View
# ---------------------------
def search_view(request):
    """Fuzzy search for products."""
    query = request.GET.get("q", "")
    products = Product.objects.all()

    if query:
        titles = list(products.values_list("title", flat=True))
        best_matches = [match[0] for match in process.extract(query, titles, limit=5, scorer=fuzz.token_sort_ratio)]

        products = products.filter(
            models.Q(title__in=best_matches)
            | models.Q(title__icontains=query)
            | models.Q(description__icontains=query)
        ).order_by("-date")

    products_with_pid = [{"product": product, "pid": product.id} for product in products]

    context = {
        "products": products,
        "query": query,
        "products_with_pid": products_with_pid
    }
    return render(request, "core/search.html", context)


# ---------------------------
# Product Detail + Add to Cart
# ---------------------------
def product_detail_view(request, pid):
    product = get_object_or_404(Product, pid=pid)

    if request.method == "POST":
        # Add to session-based cart
        cart = request.session.get("cart", {})
        cart[str(pid)] = cart.get(str(pid), 0) + 1
        request.session["cart"] = cart
        messages.success(request, f"Added {product.title} to your cart.")
        return redirect("cart")

    return render(request, "core/product_detail.html", {"product": product})

def add_to_cart(request, pid):
    product = get_object_or_404(Product, pid=pid)

    # Create a simple cart using session data
    cart = request.session.get('cart', {})

    # Increase quantity or add new
    if str(product.pid) in cart:
        cart[str(product.pid)]['quantity'] += 1
    else:
        cart[str(product.pid)] = {
            'title': product.title,
            'price': float(product.price),
            'quantity': 1,
        }

    request.session['cart'] = cart
    messages.success(request, f"{product.title} has been added to your cart.")
    return redirect('product_detail', pid=product.pid)


# ---------------------------
# Cart View
# ---------------------------
def cart_view(request):
    """Display items in cart."""
    cart = request.session.get("cart", {})
    cart_items = []
    total = Decimal("0.00")

    for pk, quantity in cart.items():
        product = get_object_or_404(Product, pk=pk)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

    return render(request, "core/cart.html", {
        "cart_items": cart_items,
        "total": total
    })


# ---------------------------
# Checkout View
# ---------------------------
@login_required
def checkout_view(request):
    """Simulate checkout using user's balance."""
    cart = request.session.get("cart", {})
    total = Decimal("0.00")

    for pk, quantity in cart.items():
        product = get_object_or_404(Product, pk=pk)
        total += product.price * quantity

    user = request.user
    success = False
    message = None

    if request.method == "POST":
        if hasattr(user, "balance") and user.balance >= total:
            user.balance -= total
            user.save()
            request.session["cart"] = {}  # clear cart
            success = True
            message = f"Purchase successful! You spent {total} coins."
        else:
            message = "Insufficient balance."

    return render(request, "core/checkout.html", {
        "total": total,
        "balance": getattr(user, "balance", 0),
        "success": success,
        "message": message
    })
