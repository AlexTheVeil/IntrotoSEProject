from django.urls import path
from userauths import views

app_name = "userauths"

urlpatterns = [
    path('register/', views.Register_View, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update_user/', views.update_user, name = 'update_user'),
    path('update_password/', views.update_password, name = 'update_password'),
]