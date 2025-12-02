from django import views
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
   path("", views.home, name ="home"),
   path("profile/", views.profile, name = "profile"),
   path("claim-daily/", views.claim_daily_ptc, name="claim_daily"),
   path("seller/", views.seller, name = "seller"),
   path("home/", views.home, name ="home"),
   path("product/<str:pid>/", views.product_detail_view, name="product_detail"),
   path("search/", views.search_view, name="search"),
   path('cart/', views.cart_view, name='cart'),
   path('add-to-cart/<str:pid>/', views.add_to_cart_view, name='add_to_cart'),
   path('cart/update/<int:item_id>/', views.update_cart_view, name='update_cart'),
   path('checkout/', views.checkout_view, name='checkout'),
   path('checkout/place-order/', views.place_order_view, name='place_order'),
   path('update_info/', views.update_info, name = 'update_info'),
   path("my_orders/", views.my_orders_view, name="my_orders"),
   # path("my_orders/my_orders/<str:order_number>/", views.order_detail, name="order_detail"),
]
