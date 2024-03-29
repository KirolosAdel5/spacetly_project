from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    
    TemplateTypeListCreateAPIView,
    TemplateTypeRetrieveUpdateDestroyView,
    TemplateSpecificationListByTypeView,
    
    TemplateSpecificationListCreateAPIView,
    TemplateSpecificationRetrieveUpdateDestroyView,
    
    TemplateListCreateAPIView,
    TemplateRetrieveUpdateDestroyView,
    TemplateFieldsAPIView,
    
    TemplateSpecificationFieldListCreateAPIView,
    TemplateSpecificationFieldRetrieveUpdateDestroyView,
    TemplateSpecificationFieldByTemplateAPIView,
    
    UserTemplateCreateAPIView,
    UserTemplateListCreateAPIView,
    UserTemplateRetrieveUpdateAPIView,
    FavoriteTemplateListCreateAPIView
)

app_name = 'spacetly_templates'

urlpatterns = [
    
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<uuid:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-retrieve-update-destroy'),
    
    path('template-types/', TemplateTypeListCreateAPIView.as_view(), name='template-type-list-create'),
    path('template-types/<int:pk>/', TemplateTypeRetrieveUpdateDestroyView.as_view(), name='template-type-list-create'),
   
    path('template-specifications/', TemplateSpecificationListCreateAPIView.as_view(), name='template-specification-list-create'),
    path('template-specifications/<int:pk>/', TemplateSpecificationRetrieveUpdateDestroyView.as_view(), name='template-specification-retrieve-update-destroy'),
    path('template-specifications/template-type/<int:template_type_id>/', TemplateSpecificationListByTypeView.as_view(), name='template-specifications-by-type'),

    path('templates/', TemplateListCreateAPIView.as_view(), name='template-list-create'),
    path('templates/<uuid:pk>/', TemplateRetrieveUpdateDestroyView.as_view(), name='template-list-create'),
    path('templates/<uuid:template_id>/fields/', TemplateFieldsAPIView.as_view(), name='template_fields_api'),

    path('template-specification-fields/', TemplateSpecificationFieldListCreateAPIView.as_view(), name='template-specification-field-list-create'),
    path('template-specification-fields/<int:pk>/', TemplateSpecificationFieldRetrieveUpdateDestroyView.as_view(), name='template-specification-field-retrieve-update-destroy'),
    path('template-specification-fields/template/<uuid:template_id>/', TemplateSpecificationFieldByTemplateAPIView.as_view(), name='template-specification-fields-by-template'),

    path('user-template/<uuid:template_id>/', UserTemplateCreateAPIView.as_view(), name='user-template-create'),
    path('user-template/', UserTemplateListCreateAPIView.as_view(), name='user-template-list'),
    path('user-templates-info/<uuid:pk>/', UserTemplateRetrieveUpdateAPIView.as_view(), name='user-template-list'),
    
    path('favorite-templates/<uuid:template_id>/', FavoriteTemplateListCreateAPIView.as_view(), name='favorite-template-create'),
    path('favorite-templates/', FavoriteTemplateListCreateAPIView.as_view(), name='favorite-template-list'),
]

from django.urls import path
