from rest_framework import generics,status,pagination 
from rest_framework.response import Response
from rest_framework.decorators import api_view
import uuid
from rest_framework import status
from .models import Document ,DocumentImage
from .serializers import DocumentSerializer , DocumentImageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .tasks import conv_chain , chat
from rest_framework.filters import SearchFilter,OrderingFilter

class DocumentPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
@api_view(['GET'])
def generate_uuid(request):
    random_uuid = uuid.uuid4()
    return Response({'uuid': str(random_uuid)})

class CreateDocument(generics.CreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        unique_id = self.kwargs.get('unique_id')

        # Check if a document with the unique_id already exists
        existing_document = Document.objects.filter(id=unique_id).first()
        if existing_document:
            # If it exists, serialize the existing document and return the serialized data
            serializer.instance = existing_document  # Set the serializer's instance attribute
            return Response(serializer.data)

        # If the unique_id doesn't exist, proceed with saving the serializer
        serializer.save(id=unique_id, user=self.request.user)

class GetUserDocuments(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DocumentPagination  
    filter_backends = [ SearchFilter,OrderingFilter]

    search_fields = ['title', 'content']
    ordering_fields = ['title','created_at','updated_at']



    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

class DeleteUserDocuments(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AddImageToDocument(generics.CreateAPIView):
    serializer_class = DocumentImageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        document_id = self.kwargs.get('document_id')
        document = Document.objects.get(pk=document_id)
        serializer.save(document=document)

class RetrieveUpdateDocument(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

class SendMessageToAIAssistant(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        
        if not message:
            return Response({'error': 'Message field is required'}, status=status.HTTP_400_BAD_REQUEST)
        response = chat(conv_chain, message)
        return Response({'response': response}, status=status.HTTP_201_CREATED)
