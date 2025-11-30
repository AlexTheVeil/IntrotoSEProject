from pyexpat.errors import messages
from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from core.models import CartOrder, Product, Category, PTCCurrencyTransaction, PTCCurrency, CartOrderItems, STATUS_CHOICE
from django.db.models import Sum
from userauths.models import User
from userauths.views import login_view, logout_view, Register_View
from django.contrib import messages
from useradmin.decorators import custom_admin_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserChangeForm
from django.forms import ModelForm
from django.core import signing
import datetime
from django import forms

# Create your views here.

def dashboard_view(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Must be logged in to view Seller Dashboard.")
        return redirect('userauths:login')
    
    products = Product.objects.filter(user=request.user)
    revenue = CartOrder.objects.aggregate(price=Sum('price'))
    total_orders_count = CartOrder.objects.all()
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    new_customers = User.objects.all()
    latest_orders = CartOrder.objects.order_by('-order_date')[:5]
    ptc_credits = PTCCurrencyTransaction.objects.filter(user=request.user,transaction_type='credit').aggregate(total_earned=Sum('amount'))['total_earned'] or 0

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
        'ptc_credits': ptc_credits,
        # signed token for vendor-specific RSS feed
        'vendor_feed_token': signing.dumps({'user_id': request.user.id}),
    }
    
    return render(request, "useradmin/dashboard.html", context)

def add_product_view(request):
    if request.method == "POST":
        title = request.POST.get("title")
        category_cid = request.POST.get("category")
        price = request.POST.get("price")
        image = request.FILES.get("image")

        if not title or not category_cid or not price or not image:
            messages.error(request, "All fields are required.")
            return redirect('useradmin:add_product')

        try:
            price = float(price)
            if price < 0:
                messages.error(request, "Price cannot be negative.")
                return redirect('useradmin:add_product')
        except ValueError:
            messages.error(request, "Invalid price format.")
            return redirect('useradmin:add_product')

        category = get_object_or_404(Category, cid=category_cid)

        product = Product(
            title=title,
            category=category,
            price=price,
            image=image,
            user=request.user  # set current user
        )
        product.save()

        # handle tags (comma separated)
        tags_input = request.POST.get('tags', '')
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            tag_objs = []
            from core.models import Tags
            for tn in tag_names:
                tag_obj, _ = Tags.objects.get_or_create(name=tn)
                tag_objs.append(tag_obj)
            if tag_objs:
                product.tags.set(tag_objs)

        messages.success(request, f"Product '{title}' added successfully!")
        return redirect('useradmin:dashboard')

    # GET request: show form
    categories = Category.objects.all()
    return render(request, "useradmin/add_product.html", {"categories": categories})

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
        # handle tags update
        tags_input = request.POST.get('tags', '')
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            tag_objs = []
            from core.models import Tags
            for tn in tag_names:
                tag_obj, _ = Tags.objects.get_or_create(name=tn)
                tag_objs.append(tag_obj)
            product.tags.set(tag_objs)
        else:
            # clear tags if field empty
            product.tags.clear()
        product.save()
        messages.success(request, f"Product '{product.title}' updated successfully.")
        return redirect("useradmin:dashboard")

    context = {
        "product": product,
        "categories": categories,
    }
    return render(request, "useradmin/edit_product.html", context)

def admin_dashboard(request):
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = CartOrder.objects.count()
    total_wallets = PTCCurrency.objects.count()

    context = {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_wallets": total_wallets,
        "pending_count": Product.objects.filter(product_status="in_review").count(),
    }

    return render(request, "useradmin/admin/dashboard.html", context)

@custom_admin_required
def admin_user_list(request):
    query = request.GET.get('q', '')  # Search query from admin UI
    if query:
        users = (User.objects.filter(username__icontains=query) |
                 User.objects.filter(email__icontains=query)).distinct().order_by('-date_joined')
    else:
        users = User.objects.all().order_by('-date_joined')

    context = {
        'users': users,
        'query': query
    }
    return render(request, 'useradmin/admin/users.html', context)


@custom_admin_required
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        # Prevent deleting self
        if request.user.id == user.id:
            messages.error(request, "You cannot delete your own account.")
            return redirect('useradmin:admin_user_list')
        user.delete()
        messages.success(request, f'User {user.username} deleted successfully.')
        return redirect('useradmin:admin_user_list')
    return render(request, 'useradmin/admin/confirm_delete.html', {'user': user})


@custom_admin_required
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('useradmin:admin_user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserChangeForm(instance=user)

    context = {
        'form': form,
        'user_obj': user
    }
    return render(request, 'useradmin/admin/edit_user.html', context)


@custom_admin_required
def admin_toggle_user_staff(request, user_id):
    # Toggle a user's is_staff status (promote/demote) — admin only
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('useradmin:admin_user_list')

    # Prevent demoting yourself accidentally
    if request.user.id == user_id:
        messages.error(request, "You cannot change your own admin status.")
        return redirect('useradmin:admin_user_list')

    target = get_object_or_404(User, id=user_id)
    # Toggle is_staff
    target.is_staff = not bool(target.is_staff)
    target.save()
    status = 'promoted to admin' if target.is_staff else 'demoted from admin'
    messages.success(request, f"User '{target.username}' has been {status}.")
    return redirect('useradmin:admin_user_list')

@custom_admin_required
def admin_product_list(request):
    products = Product.objects.all().order_by('-date')
    context = {
        'products': products
    }
    return render(request, 'useradmin/admin/products.html', context)

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'category', 'price', 'old_price', 
                  'product_status', 'in_stock', 'featured', 'image', 'specifications']

def admin_edit_product(request, pid):
    product = get_object_or_404(Product, pid=pid)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product {product.title} updated successfully.')
            return redirect('useradmin:admin_product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)

    context = {'form': form, 'product_obj': product}
    return render(request, 'useradmin/admin/edit_product.html', context)

@custom_admin_required
def admin_delete_product(request, pid):
    # Admin-only deletion of any product
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('useradmin:admin_product_list')

    product = get_object_or_404(Product, pid=pid)
    product.delete()
    messages.success(request, f"Product '{product.title}' was deleted.")
    return redirect('useradmin:admin_product_list')

def admin_order_list(request):
    orders = CartOrder.objects.all().order_by('-order_date')
    context = {
        'orders': orders
    }
    return render(request, 'useradmin/admin/orders.html', context)

def admin_order_detail(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id)
    items = CartOrderItems.objects.filter(order=order)
    context = {
        'order': order,
        'items': items
    }
    return render(request, 'useradmin/admin/order_detail.html', context)

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = CartOrder
        fields = ['product_status']
        widgets = {
            'product_status': forms.Select(choices=STATUS_CHOICE)
        }

def admin_order_update(request, order_id):
    order = get_object_or_404(CartOrder, id=order_id)
    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f"Order #{order.id} status updated successfully.")
            return redirect('useradmin:admin_order_list')
    else:
        form = OrderStatusForm(instance=order)

    context = {'form': form, 'order': order}
    return render(request, 'useradmin/admin/order_update.html', context)

def admin_ptc_dashboard(request):
    wallets = PTCCurrency.objects.select_related('user').all()
    context = {'wallets': wallets}
    return render(request, 'useradmin/admin/ptc.html', context)

def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('useradmin:admin_dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('useradmin:admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or you are not an admin.")

    return render(request, "useradmin/admin/login.html")

def admin_review_products(request):
    products = Product.objects.filter(product_status="in_review")
    context = {"products": products}
    return render(request, "useradmin/admin/review_products.html", context)

def admin_product_approve(request, pid):
    product = get_object_or_404(Product, pid=pid)
    product.product_status = "published"
    product.save()
    messages.success(request, f"Product '{product.title}' approved and published.")
    return redirect("useradmin:admin_review_products")

def admin_product_deny(request, pid):
    product = get_object_or_404(Product, pid=pid)
    product.product_status = "rejected"
    product.save()
    messages.success(request, f"Product '{product.title}' has been denied.")
    return redirect("useradmin:admin_review_products")


@login_required
def seller_delete_product(request, pid):
    # Allow product owner to delete their rejected product to free up space
    product = get_object_or_404(Product, pid=pid)
    if product.user != request.user:
        messages.error(request, "You don't have permission to delete this product.")
        return redirect('useradmin:dashboard')

    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('useradmin:dashboard')

    # Only allow deletion if product was rejected (or owner explicitly wants to remove)
    if product.product_status != 'rejected':
        messages.error(request, "Only rejected products can be removed here.")
        return redirect('useradmin:dashboard')

    product.delete()
    messages.success(request, f"Product '{product.title}' has been removed.")
    return redirect('useradmin:dashboard')