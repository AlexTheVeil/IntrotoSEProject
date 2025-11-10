from django import views
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
   path("", views.base, name ="base"),
   path("buyer/", views.buyer, name = "buyer"),
   path("seller/", views.seller, name = "seller"),
   path("home/", views.home, name ="home"),
   path("product/<str:pid>/", views.product_detail_view, name="product_detail"),
   path("search/", views.search_view, name="search"),
   path('cart/', views.cart_view, name='cart'),
   path('add-to-cart/<str:pid>/', views.add_to_cart_view, name='add_to_cart'),
   path('cart/update/<int:item_id>/', views.update_cart_view, name='update_cart'),
   path('checkout/', views.checkout_view, name='checkout'),
   path('checkout/place-order/', views.place_order_view, name='place_order'),
]
