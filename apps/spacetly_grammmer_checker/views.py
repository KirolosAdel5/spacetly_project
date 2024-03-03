from rest_framework import generics,status,pagination 
from rest_framework.decorators import api_view,permission_classes
from .models import Document, DocumentImage, DocumentFile
from .serializers import DocumentSerializer, DocumentImageSerializer, DocumentFileSerializer
from rest_framework.response import Response
from .tasks import correct_the_grammar_mistakes
import ast
import uuid
from django.shortcuts import get_object_or_404
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from rest_framework.permissions import IsAuthenticated
import json
from adawat import adaat
class DocumentPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CheckMistakesAPIView(generics.UpdateAPIView):
    def post(self, request, unique_id, *args, **kwargs):
        document, created = Document.objects.get_or_create(unique_id=unique_id, created_by=request.user)
        if created:
            document.save()
       
        # Get the text from the request data
        text = request.data.get('content', '')
        
        # Correct grammar mistakes
        mistakes =  correct_the_grammar_mistakes(text)
        document.mistakes =  mistakes

        # Serialize the updated document data
        serializer = DocumentSerializer(instance=document, data=request.data)
        
        # Validate and save the updated document
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    lookup_field = 'unique_id'  # Specify the lookup field
    pagination_class = DocumentPagination  # Add pagination class
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Document.objects.filter(created_by=self.request.user)
    def create(self, request, *args, **kwargs):
        unique_id = uuid.uuid4()
        return Response({'unique_id': unique_id}, status=status.HTTP_201_CREATED)

class DocumentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    lookup_field = 'unique_id'  # Specify the lookup field

    def get_queryset(self):
        return Document.objects.filter(unique_id=self.kwargs['unique_id'])

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        return super().update(request, *args, **kwargs)

class DocumentImageViewSet(generics.ListCreateAPIView):
    serializer_class = DocumentImageSerializer

    def get_queryset(self):
        unique_id = self.kwargs['unique_id']
        return DocumentImage.objects.filter(document__unique_id=unique_id)

    def perform_create(self, serializer):
        unique_id = self.kwargs['unique_id']
        document = get_object_or_404(Document, unique_id=unique_id)
        serializer.save(document=document)

class DocumentImageDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = DocumentImage.objects.all()
    serializer_class = DocumentImageSerializer

class DocumentFileViewSet(generics.ListCreateAPIView):
    serializer_class = DocumentFileSerializer

    def get_queryset(self):
        unique_id = self.kwargs['unique_id']
        return DocumentFile.objects.filter(document__unique_id=unique_id)

    def perform_create(self, serializer):
        unique_id = self.kwargs['unique_id']
        document = get_object_or_404(Document, unique_id=unique_id)
        serializer.save(document=document)

class DocumentFileDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    queryset = DocumentFile.objects.all()
    serializer_class = DocumentFileSerializer

@api_view(['GET'])
def read_document_file(request, document_id, file_id):
    try:
        document = Document.objects.get(unique_id=document_id)
        file = DocumentFile.objects.get(id=file_id, document=document)
    except (Document.DoesNotExist, DocumentFile.DoesNotExist):
        return Response({'error': 'Document or file not found'}, status=status.HTTP_404_NOT_FOUND)

    # Extract text from the file
    if file.file.name.endswith('.docx'):
        text = read_word_file(file.file)
    elif file.file.name.endswith('.pdf'):
        text = read_pdf(file.file)
    else:
        return Response({'error': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Proofread the extracted text
    proofread_result = text  # Assuming proofread_text() function exists
    return Response({'text': proofread_result})

def read_word_file(uploaded_file):
    full_text = []
    with uploaded_file.open('rb') as file:
        doc = DocxDocument(file)
        for para in doc.paragraphs:
            full_text.append(para.text)
    return '\n'.join(full_text)

def read_pdf(uploaded_file):
    text = ""
    with uploaded_file.open('rb') as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tashkeel_text_APIView(request):
    if request.method == 'POST':
        try:
            text = request.data.get('text')
            lastmark = True if request.data.get('lastmark') == 'True' else False
            if text:
                text_t = adaat.tashkeel_text(text, lastmark)
                return Response({'tashkeel_text': text_t}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Text field is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_tashkeel_text_APIView(request):
    if request.method == 'POST':
        try:
            text = request.data.get('text')
            lastmark = True if request.data.get('lastmark') == 'True' else False
            if text:
                text_t = adaat.normalize(text)
                return Response({'normal_text': text_t}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Text field is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
