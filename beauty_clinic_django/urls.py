"""
URL configuration for beauty_clinic_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from . import views
from appointments.views import get_notifications_api, update_notifications_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', include('accounts.urls', namespace='login')),  # Handles /login/ patterns
    # Social auth (django-allauth) - include FIRST to ensure allauth URLs are registered before custom accounts URLs
    # Allauth provides URLs like /accounts/social/google/login/ and expects 'socialaccount_login' URL name
    path('accounts/', include('allauth.urls')),
    # Custom accounts URLs - comes after allauth to avoid conflicts, but custom patterns take precedence
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('services/', include('services.urls')),
    path('products/', include('products.urls')),
    path('packages/', include('packages.urls')),
    path('appointments/', include('appointments.urls')),
    path('analytics/', include('analytics.urls')),
    path('attendant/', include('attendant.urls')),
    path('owner/', include('owner.urls')),
    
    # Global notification API endpoints (for pages that don't have their own)
    path('notifications/get_notifications.php', get_notifications_api, name='global_get_notifications'),
    path('notifications/update_notifications.php', update_notifications_api, name='global_update_notifications'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
