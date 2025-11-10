from pyexpat.errors import messages
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
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        image = request.FILES.get('image')  # For uploaded files

        # Basic validation
        if not name or not category_id or not price:
            messages.error(request, "Please fill out all required fields.")
            return redirect('useradmin:add_product')
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Selected category does not exist.")
            return redirect('useradmin:add_product')

        try:
            price = float(price)
        except ValueError:
            messages.error(request, "Invalid price entered.")
            return redirect('useradmin:add_product')

        # Create the product
        Product.objects.create(
            name=name,
            category=category,
            price=price,
            image=image
        )

        messages.success(request, f"Product '{name}' has been added successfully!")
        return redirect('useradmin:dashboard')  # Back to dashboard

    # GET request: display the form
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'useradmin/add_product.html', context)