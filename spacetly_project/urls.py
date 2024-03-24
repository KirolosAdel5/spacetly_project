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
    path('api/v1/text-rephrase/', include('apps.spacetly_text_rephrase.urls',namespace="spacetly_text_rephrase")),
    path('api/v1/grammmer-checker/', include('apps.spacetly_grammmer_checker.urls',namespace="spacetly_grammmer_checker")),
    path('api/v1/templates/', include('apps.spacetly_templates.urls',namespace="spacetly_templates")),
    path('api/v1/image-generator/', include('apps.image_generator.urls',namespace="image_generator")),
    path('api/admin-dash/', include('apps.admin_dash.urls',namespace="admin_dash")),
    path('api/v1/writing-assistant/', include('apps.ai_document_editor.urls',namespace="ai_document_editor")),
    path('api/v1/chat-doc/', include('apps.chat_docs.urls',namespace="chat_docs")),
    path('api/v1/spacetly_articleGenerator/', include('apps.spacetly_articleGenerator.urls',namespace="spacetly_articleGenerator")),
    path('api/v1/mutqin_assistant/', include('apps.mutqin_assistant.urls',namespace="mutqin_assistant")),
    
    ]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
