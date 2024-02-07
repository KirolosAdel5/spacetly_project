from django.contrib import admin
from django.urls import path,include

from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view()),
    
    path('api/', include('apps.users.urls',namespace="spacetly_users")),
    path('api/v1/chatbot/', include('apps.spacetly_chatbot.urls',namespace="spacetly_chatbot")),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
