from django.urls import path , include
from .views import *

app_name = 'mutqin_assistant'

urlpatterns = [
    path('generate-id/', generate_uuid, name='generate_id'),

    path('<uuid:document_id>/', MutqinAssistantCreateView.as_view(), name='mutqin_assistant_create'),
    path('all_templates/', MutqinAssistantListView.as_view(), name='mutqin_assistant_list'),
    
    path('<uuid:pk>/detail/', MutqinAssistantDetailView.as_view(), name='mutqin_assistant_detail'),

]
