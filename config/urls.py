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
    path('api/banknotes/', include('banknotes.urls')),
    # Remaining collection modules — enable after full install:
    # path('api/seals/', include('seals.urls')),
    # path('api/tasbih/', include('tasbih.urls')),
    # path('api/rings/', include('rings.urls')),
    # path('api/knives/', include('knives.urls')),
    # path('api/antiques/', include('antiques.urls')),
    # path('api/stamps/', include('stamps.urls')),
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
