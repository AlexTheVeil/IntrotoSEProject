
from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("product/<slug:slug>", views.product_detail, name="product_detail"),
    path("seller/", views.seller_dashboard, name="seller_dashboard"),
    path("seller/payouts/", views.payout_list, name="payout_list"),
    path("seller/payouts/request/", views.payout_request, name="payout_request"),
]
