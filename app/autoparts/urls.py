"""autoparts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

API_PREFIX = 'api'
DOCS_PREFIX = 'docs'
DEFAULT_API_VERSION = 'v1'

schema_view = get_schema_view(
    openapi.Info(
        title=settings.DRF_YASG['PROJECT_NAME'],
        default_version=DEFAULT_API_VERSION,
        description=settings.DRF_YASG['DESCRIPTION'],
    ),
    public=True
)

# REST API V1 urls
api_v1_urlpatterns = [
    path(f"{API_PREFIX}/{DEFAULT_API_VERSION}/ebay/",
         include(('ebay.api.v1.urls', 'ebay'), namespace=DEFAULT_API_VERSION), name='ebay')
]

# simplejwt urls
jwt_urlpatterns = [
    path(f"{API_PREFIX}/{DEFAULT_API_VERSION}/token/", TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(f"{API_PREFIX}/{DEFAULT_API_VERSION}/token/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path(f"{API_PREFIX}/{DEFAULT_API_VERSION}/token/verify/", TokenVerifyView.as_view(), name='token_verify'),
]

# drf-yasg
drf_yasg_urlpatterns = [
    url(r'^api/v1/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^api/v1/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^api/v1/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Media & static files urls
static_media_urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
                           + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Apps urls
apps_urlpatterns = [
    path('ebay/', include('ebay.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns = api_v1_urlpatterns \
              + jwt_urlpatterns \
              + static_media_urlpatterns \
              + apps_urlpatterns

if settings.DEBUG:
    urlpatterns += drf_yasg_urlpatterns
