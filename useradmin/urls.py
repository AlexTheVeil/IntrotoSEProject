from django.urls import path
from useradmin import views
from .views import login_view, logout_view, Register_View

app_name = "useradmin"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path('add-product/', views.add_product_view, name='add_product'), 
    path('edit-product/<str:pid>/', views.edit_product, name='edit_product'),
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/users/", views.admin_user_list, name="admin_user_list"),
    path("admin-panel/products/", views.admin_product_list, name="admin_product_list"),
    path("admin-panel/orders/", views.admin_order_list, name="admin_order_list"),
    path("admin-panel/ptc/", views.admin_ptc_dashboard, name="admin_ptc_dashboard"),
    
]
