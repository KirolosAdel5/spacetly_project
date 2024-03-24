from django.urls import path
from . import views
app_name = 'chat_docs'

urlpatterns = [
    
    # List and create documents
    path('documents/', views.DocumentsListCreate.as_view(), name='documents-list-create'),
    path('documents/<uuid:pk>/', views.DocumentDetail.as_view(), name='document-detail'),

    # Favourite a document
    path('documents/<uuid:pk>/favourite/', views.DocumentFavourite.as_view(), name='document-favourite'),
    # Archive a document
    path('documents/<uuid:pk>/archive/', views.DocumentArchive.as_view(), name='document-archive'),

    # List messages in a document
    path('documents/<uuid:document_id>/messages/', views.MessageList.as_view(), name='message-list'),

    # Create a message in a document
    path('documents/<uuid:document_id>/messages/create/', views.MessageCreate.as_view(), name='message-create'),
    
    # async gpt task
    # path('documents/task/<str:task_id>/', views.GPT3TaskStatus.as_view(), name='gpt_task_status'),

]