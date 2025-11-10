from django.urls import path
from useradmin import views
from .views import login_view, logout_view, Register_View

app_name = "useradmin"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path('add-product/', views.add_product_view, name='add_product'), 
]
