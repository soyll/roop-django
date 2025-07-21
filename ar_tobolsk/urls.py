from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/', include('faceswap.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)