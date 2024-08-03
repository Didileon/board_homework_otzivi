from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('profile/', include("profiles.urls")),
    path("accounts/", include("allauth.urls")),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path("accounts/", include("accounts.urls")),
    path('', include("config.urls")),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)