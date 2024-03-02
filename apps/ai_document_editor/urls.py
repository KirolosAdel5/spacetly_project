from django.urls import path
from . import views
app_name = 'ai_document_editor'

urlpatterns = [
    path('generate-id/', views.generate_uuid, name='generate_id'),
    path('create-document/<uuid:unique_id>/', views.CreateDocument.as_view(), name='create_document'),
    path('get_user_documents/', views.GetUserDocuments.as_view(), name='get_user_documents'),
    path('delete_user_documents/', views.DeleteUserDocuments.as_view(), name='delete_user_documents'),
    path('add_image_to_document/<uuid:document_id>/', views.AddImageToDocument.as_view(), name='add_image_to_document'),
    path('document/<uuid:pk>/', views.RetrieveUpdateDocument.as_view(), name='retrieve_update_destroy_document'),
    path('send-message-to-ai/', views.SendMessageToAIAssistant.as_view(), name='send_message_to_ai'),

]
