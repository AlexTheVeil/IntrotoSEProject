from django.urls import path
from useradmin import views
from .views import login_view, logout_view, Register_View
# from .feeds import VendorOrderFeed  # Temporarily commented out for testing

app_name = "useradmin"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path('add-product/', views.add_product_view, name='add_product'), 
    path('edit-product/<str:pid>/', views.edit_product, name='edit_product'),
    path("admin-login/", views.admin_login_view, name="admin_login"),
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/users/", views.admin_user_list, name="admin_user_list"),
    path("admin-panel/users/delete/<int:user_id>/", views.admin_delete_user, name="admin_delete_user"),
    path("admin-panel/users/edit/<int:user_id>/", views.admin_edit_user, name="admin_edit_user"),
    path("admin-panel/users/toggle-admin/<int:user_id>/", views.admin_toggle_user_staff, name="admin_toggle_user_staff"),
    path("admin-panel/users/ban/<int:user_id>/", views.admin_ban_user, name="admin_ban_user"),
    path("admin-panel/users/unban/<int:user_id>/", views.admin_unban_user, name="admin_unban_user"),
    path("admin-panel/products/", views.admin_product_list, name="admin_product_list"),
    path("admin-panel/products/edit/<str:pid>/", views.admin_edit_product, name="admin_edit_product"),
    path("admin-panel/products/delete/<str:pid>/", views.admin_delete_product, name="admin_delete_product"),
    # vendor RSS feed (signed token ensures only recipient of token can access)
    path('feeds/vendor/<int:user_id>/<str:token>/', views.vendor_order_feed, name='vendor_order_feed'),
    path("admin-panel/orders/", views.admin_order_list, name="admin_order_list"),
    path("admin-panel/orders/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path("admin-panel/orders/<int:order_id>/update/", views.admin_order_update, name="admin_order_update"),
    path("admin-panel/ptc/", views.admin_ptc_dashboard, name="admin_ptc_dashboard"),
    path("admin-panel/review-products/", views.admin_review_products, name="admin_review_products"),
    path("admin-panel/review-products/approve/<str:pid>/", views.admin_product_approve, name="admin_product_approve"),
    path("admin-panel/review-products/deny/<str:pid>/", views.admin_product_deny, name="admin_product_deny"),
    path('delete-product/<str:pid>/', views.seller_delete_product, name='seller_delete_product'),
]
