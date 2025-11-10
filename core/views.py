from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from core.models import Category, Tags, Vendor, Product, ProductImages, CartOrder, CartOrderItems, ProductReview, Wishlist, Address
from django.db.models import Q

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