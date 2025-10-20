from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "available", "created_at")
    list_filter = ("available",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

