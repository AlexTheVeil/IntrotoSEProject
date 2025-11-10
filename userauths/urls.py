from django.urls import path
from userauths import views

app_name = "userauths"

urlpatterns = [
    path('register/', views.Register_View, name='register'),
]