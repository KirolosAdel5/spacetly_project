from django.urls import path
from .views import (
    TextListCreate,
    RephraseTextView,
    TextDetail,
    TextRepharseImagesView,
    TextRepharseImageDetailView
    )

app_name = 'spacetly_text_rephrase' 

urlpatterns = [
    # List and create text rephrase
    path('texts/', TextListCreate.as_view(), name='create_empty_text'),
    path('texts/<uuid:unique_id>/', TextDetail.as_view(), name='text_detail'),
    
    path('create/<uuid:unique_id>/', RephraseTextView.as_view(), name='rephrase_text'),
    path('texts/<uuid:unique_id>/images/', TextRepharseImagesView.as_view(), name='upload_image'),
    path('texts/<uuid:unique_id>/images/<int:image_id>/', TextRepharseImageDetailView.as_view(), name='text_repharse_image_detail'),


]
