"""
URL configuration for base project.

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
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings

admin.site.site_title = 'SENDIT'
admin.site.site_header = 'Welcome to SENDIT Admin site'
admin.site.index_title = 'Site admin'

first_version = [
    path("", include("apps.core.urls")),
    path('users/', include('apps.account.urls')),
    path('offers/', include('apps.offers.urls')),
    path('payments/', include('apps.payments.urls')),
    path("wallets/", include('apps.wallets.urls')),
    path('escrows/', include('apps.escrow.urls')),
    path('landing/', include('apps.landing.urls')),
    # path('payouts/', include('apps.payouts.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(first_version)),

    # drf spectacular for documentation
    path('api/doc/', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(), name='redoc'),
    path('', SpectacularSwaggerView.as_view(
        url_name='schema'), name='swagger-ui'),
    
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

