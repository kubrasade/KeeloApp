from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/auth/', include('authub.urls')),
    path('api/match/', include('match.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/meal/', include('meal.urls')),
    path('api/traning/',include('traning.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
