"""
URL configuration for DigitalBooking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.i18n import set_language
from . import views

admin.site.site_header = 'Digital Booking Admin'
admin.site.site_title = 'Digital Booking Admin'
admin.site.index_title = 'Welcome to Digital Booking Admin'

urlpatterns = [
    path('set_language/', set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('', include('user.urls')),
    path('movie/', include('movie.urls')),
    path('', include('services.urls')),
    path('payment/', include('payment.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
