from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from core.models import Category, Tags, Vendor, Product, ProductImages, CartOrder, CartOrderItems, ProductReview, Wishlist, Address


def base(request):
    return render(request, 'core/base.html',)

def home(request):
    # Only show active products, newest first
    products = Product.objects.filter(status=True).order_by('-date')

    context = {
        'products': products,
    }
    return render(request, 'core/home.html', context)


