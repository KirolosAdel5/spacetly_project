from django.urls import path , include
from .views import ImageGeneCreateView,RetrieveAllImagesView , RetrieveSpecificImageView, RemoveImageView 
from rest_framework.routers import DefaultRouter

app_name = 'image_generator'

urlpatterns = [
    # List and create conversations
    path('create/', ImageGeneCreateView.as_view(), name='image-gene-create'),
    # Retrieve, update, and delete a specific conversation
    path('images/', RetrieveAllImagesView.as_view(), name='retrieve_all_images'),
    path('images/<uuid:image_id>/', RetrieveSpecificImageView.as_view(), name='retrieve_specific_image'),
    path('images/<uuid:image_id>/remove/', RemoveImageView.as_view(), name='remove_image'),
   
    # path('specific-image/<uuid:image_id>/image/<uuid:pk>/', RetrieveSingleImageView.as_view(), name='retrieve_specific_image'),
    # path('specific-image/<uuid:image_id>/image/<uuid:pk>/delete', DeleteSingleImageView.as_view(), name='delete_specific_image'),

    
]
