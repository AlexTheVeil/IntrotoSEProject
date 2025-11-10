from django import views
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
   path("", views.base, name ="base"),
   path("home/", views.home, name ="home"),
   path("product/<str:pid>/", views.product_detail_view, name="product_detail"),
]
