"""
URL configuration for config project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/medals/', include('medals.urls')),
    path('api/coins/', include('coins.urls')),
    # Collection modules (banknotes/seals/tasbih/rings/knives/antiques/stamps)
    # enabled after full source is installed via:
    #   python scripts/bootstrap_collection_modules.py
    path('api/reports/', include('reports.urls')),
]

if settings.DEBUG or getattr(settings, 'SPECTACULAR_SERVE_PUBLIC', False):
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path(
            'api/swagger/',
            SpectacularSwaggerView.as_view(url_name='schema'),
            name='swagger-ui',
        ),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
