from pyexpat.errors import messages
from urllib import request
from django.shortcuts import render, redirect
from core.models import CartOrder, Product, Category
from django.db.models import Sum
from userauths.models import User
from userauths.views import login_view, logout_view, Register_View

import datetime

# Create your views here.

def dashboard_view(request):
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