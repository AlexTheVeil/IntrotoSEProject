from pyexpat.errors import messages
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from core.models import CartOrder, Product, Category
from django.db.models import Sum
from userauths.models import User
from userauths.views import login_view, logout_view, Register_View

import datetime

# Create your views here.

def dashboard_view(request):
    products = Product.objects.filter(user=request.user)
    revenue = CartOrder.objects.aggregate(price=Sum('price'))
    total_orders_count = CartOrder.objects.all()
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    new_customers = User.objects.all()
    latest_orders = CartOrder.objects.order_by('-order_date')[:5]

    this_month = datetime.datetime.now().month

    montly_revenue = CartOrder.objects.filter(order_date__month=this_month).aggregate(price=Sum('price'))

    context = {
        'revenue': revenue,
        'total_orders_count': total_orders_count,
        'all_products': all_products,
        'all_categories': all_categories,
        'new_customers': new_customers,
        'latest_orders': latest_orders,
        'montly_revenue': montly_revenue,
        'products' : products,
    }
    
    return render(request, 'useradmin/dashboard.html', context)

def add_product_view(request):
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        price = request.POST.get("price")
        image = request.FILES.get("image")

        category = Category.objects.filter(id=category_id).first()
        if not category:
            messages.error(request, "Please select a valid category.")
            return redirect("useradmin:add_product")

        Product.objects.create(
            name=name,
            category=category,
            price=price,
            image=image,
        )

        messages.success(request, f"Product '{name}' added successfully!")
        return redirect("useradmin:dashboard")

    context = {
        "categories": categories,
    }
    return render(request, "useradmin/add_product.html", context)

def edit_product(request, pid):
    product = get_object_or_404(Product, pid=pid)

    # Optional: Restrict editing to the vendor who owns it
    if product.user != request.user:
        messages.error(request, "You don’t have permission to edit this product.")
        return redirect("useradmin:dashboard")

    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        specifications = request.POST.get("specifications")
        image = request.FILES.get("image")

        product.title = title
        product.description = description
        product.price = price
        product.specifications = specifications

        if category_id:
            category = Category.objects.filter(cid=category_id).first()
            if category:
                product.category = category

        if image:
            product.image = image

        product.save()
        messages.success(request, f"Product '{product.title}' updated successfully.")
        return redirect("useradmin:dashboard")

    context = {
        "product": product,
        "categories": categories,
    }
    return render(request, "useradmin/edit_product.html", context)