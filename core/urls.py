from django import views
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
   path("", views.base, name ="base"),
   path("home/", views.home, name ="home"),
   path("product/<str:pid>/", views.product_detail_view, name="product_detail"),
   path("search/", views.search_view, name="search"),
   path('cart/', views.cart_view, name='cart'),
   path('add-to-cart/<str:pid>/', views.add_to_cart_view, name='add_to_cart')

]
