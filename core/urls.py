from django.urls import path
from core.views import base

app_name = 'core'

urlpatterns = [
   path("", base, name ="base"),
]
