# views.py
from rest_framework import generics
from .models import MutqinAssistant
from ..ai_document_editor.models import Document
from .serializers import MutqinAssistantSerializer
from .tasks import do_prompt
import uuid
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.filters import SearchFilter,OrderingFilter

@api_view(['GET'])
def generate_uuid(request):
    document_id = uuid.uuid4()
    template_id = uuid.uuid4()

    # Return the UUIDs as a response
    return Response({'document_id': str(document_id), 'template_id': str(template_id)})

class LastTemplatesPagination(LimitOffsetPagination):
    """
    Pagination class for last templates.
    """
    default_limit = 10
    max_limit = 10

class MutqinAssistantListView(generics.ListAPIView):
    queryset = MutqinAssistant.objects.all()
    serializer_class = MutqinAssistantSerializer
    permission_classes = [IsAuthenticated]
    pagination_class =  LastTemplatesPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['template', 'question', 'language', 'content']  # Define fields to search
  
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class MutqinAssistantCreateView(generics.CreateAPIView):
    queryset = MutqinAssistant.objects.all()
    serializer_class = MutqinAssistantSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        document_id = self.kwargs.get('document_id')

        if 'template_name' not in request.query_params or 'h_i' not in request.query_params:
            return Response({"error": "You must provide both 'template_name' and template id 'h_i'."}, status=status.HTTP_400_BAD_REQUEST)
        
        template_name = request.query_params.get('template_name')
        template_id = request.query_params.get('h_i')
        
        if 'question' not in request.data or 'language' not in request.data or 'title' not in request.data:
            return Response({"error": "You must provide both 'question' , 'language' and 'title'."}, status=status.HTTP_400_BAD_REQUEST)
        
        question = request.data.get('question')
        language = request.data.get('language')
        title = request.data.get('title')
        

        response = do_prompt(question, language)
        
        # Create or get the document
        document, created = Document.objects.get_or_create(id=document_id, user=request.user)
        document.content = response
        document.title = title
        document.save()
        
        mutqin_assistant =  MutqinAssistant.objects.get_or_create(id=template_id, document=document, user=request.user)[0]
        try:            
            # Update existing MutqinAssistant
            mutqin_assistant.document = document
            mutqin_assistant.template = template_name
            mutqin_assistant.question = question
            mutqin_assistant.language = language
            mutqin_assistant.content = response
            mutqin_assistant.user = request.user
            mutqin_assistant.save()
            
            serializer = self.get_serializer(mutqin_assistant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except :
            return Response({"error": "Failed to update MutqinAssistant."}, status=status.HTTP_400_BAD_REQUEST)


class MutqinAssistantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MutqinAssistant.objects.all()
    serializer_class = MutqinAssistantSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        document_id = instance.document_id
        document = Document.objects.get(id=document_id)
        if 'content' in request.data:
            new_content = request.data.get('content')
            # Update the associated document's content
            document.content = new_content
            document.save()
            instance.content = new_content
            instance.save()
        
        if 'title' in request.data:
            new_title = request.data.get('title')
            # Update the associated document's title
            document.title = new_title
            document.save()
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            self.perform_destroy(instance)
            return Response({"message": "MutqinAssistant template was successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "MutqinAssistant template not found."}, status=status.HTTP_404_NOT_FOUND)
