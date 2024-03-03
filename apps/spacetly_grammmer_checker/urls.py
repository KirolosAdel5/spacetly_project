from django.urls import path
from .views import (
    DocumentListCreateAPIView,
    DocumentRetrieveUpdateDestroyAPIView,
    DocumentImageViewSet,
    DocumentImageDetailViewSet,
    DocumentFileViewSet,
    DocumentFileDetailViewSet,
    CheckMistakesAPIView,
    tashkeel_text_APIView,
    remove_tashkeel_text_APIView,
    read_document_file
)
app_name = 'spacetly_grammmer_checker'

urlpatterns = [
    # Document URLs
    path('documents/', DocumentListCreateAPIView.as_view(), name='document-list'),
    path('documents/<uuid:unique_id>/', DocumentRetrieveUpdateDestroyAPIView.as_view(), name='document-detail'),
    
    path('check-mistakes/<uuid:unique_id>/', CheckMistakesAPIView.as_view(), name='check-mistakes-by-unique-id'),
    path('tashkeel_text/', tashkeel_text_APIView, name='tashkeel_text'),
    path('remove_tashkeel_text/', remove_tashkeel_text_APIView, name='remove_tashkeel_text'),
    # DocumentImage URLs
    path('upload/image/<uuid:unique_id>/', DocumentImageViewSet.as_view(), name='upload_image'),
    path('document/<uuid:unique_id>/image/<int:pk>/', DocumentImageDetailViewSet.as_view(), name='document_image_detail'),


    # DocumentFile URLs
    path('upload/file/<uuid:unique_id>/', DocumentFileViewSet.as_view(), name='upload_file'),
    path('document/<uuid:unique_id>/file/<int:pk>/', DocumentFileDetailViewSet.as_view(), name='document_file_detail'),

    # read text from file
    path('document/<uuid:document_id>/file/<int:file_id>/read/', read_document_file, name='read_document_file'),

]
