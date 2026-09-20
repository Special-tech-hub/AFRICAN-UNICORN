"""
Root URL configuration for TakeOFF Driver Onboarding Platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Health check
    path('health/', include('core.urls')),

    # API routes
    path('api/auth/', include('apps.accounts.urls', namespace='accounts')),
    path('api/driver/', include('apps.onboarding.urls', namespace='onboarding')),
    path('api/driver/documents/', include('apps.documents.urls', namespace='documents')),
    path('api/applications/', include('apps.applications.urls', namespace='applications')),
    path('api/admin/', include('apps.reviews.urls', namespace='reviews')),
    path('api/notifications/', include('apps.notifications.urls', namespace='notifications')),

    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
