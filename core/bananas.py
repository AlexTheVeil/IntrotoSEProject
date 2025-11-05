from django.urls import path
from core.views import index
from . import views

app_name = "bananas"

urlpatterns = [
    path("bananas/", views.index, name = 'index')
]