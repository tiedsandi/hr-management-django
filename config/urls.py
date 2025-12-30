"""
URL configuration for config project.

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
from django.urls import include, path
from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView

from api.schema_views import SpectacularAPIViewV1, SpectacularAPIViewV2

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # API Routes
    path('api/', include(('api.urls', 'api'), namespace='api')),
    
    # OpenAPI/Swagger Documentation - V1
    path('api/v1/schema/', SpectacularAPIViewV1.as_view(), name='schema-v1'),
    path('api/v1/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema-v1'), name='swagger-ui-v1'),
    path('api/v1/schema/redoc/', SpectacularRedocView.as_view(url_name='schema-v1'), name='redoc-v1'),
    
    # OpenAPI/Swagger Documentation - V2
    path('api/v2/schema/', SpectacularAPIViewV2.as_view(), name='schema-v2'),
    path('api/v2/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema-v2'), name='swagger-ui-v2'),
    path('api/v2/schema/redoc/', SpectacularRedocView.as_view(url_name='schema-v2'), name='redoc-v2'),
]
