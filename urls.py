# core/urls.py  or store/urls.py
from django.urls import path
from . import views
from core.views import search_view

urlpatterns = [
    #add_product view
    path('add-product/', views.add_product, name='add_product'),

    #search bar
    path("search/", views.search_view, name='home'),

    #temp home
    path('', views.home, name='home'),
]
