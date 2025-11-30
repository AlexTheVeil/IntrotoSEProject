"""
URL configuration for IntrotoSEProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import base
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Mount Django's built-in auth URLs under /user/ so paths like
    # /user/login/ and /user/logout/ are available.
    path('user/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
    path("", base),
    # Authentication URLs (single include with namespace)
    path('userauths/', include(('userauths.urls', 'userauths'), namespace='userauths')),

    # Admin panel for vendors/site admins — include with namespace so
    # `{% url 'useradmin:...' %}` works in templates.
    path("useradmin/", include(('useradmin.urls', 'useradmin'), namespace='useradmin')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




