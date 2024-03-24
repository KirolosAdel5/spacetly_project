from rest_framework import generics ,status
from rest_framework.views import APIView

from rest_framework.response import Response
from .models import Text,TextRepharseImage
from .serializers import TextSerializer,TextRepharseImageSerializer
from rest_framework.permissions import IsAuthenticated
from .tasks import rephrase
from django.utils import timezone
import requests
from bs4 import BeautifulSoup
import uuid
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

class LastMessagesPagination(LimitOffsetPagination):
    """
    Pagination class for last messages.
    """
    default_limit = 10
    max_limit = 10

class TextListCreate(generics.ListCreateAPIView):
    queryset = Text.objects.all()
    serializer_class = TextSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'unique_id'  # Specify the lookup field as unique_id
    pagination_class = LastMessagesPagination
    
    def get_queryset(self):
        return Text.objects.filter(created_by=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        # Generate a random UUID
        unique_id = uuid.uuid4()
        return Response({'unique_id': unique_id}, status=status.HTTP_201_CREATED)
    
class RephraseTextView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, unique_id, *args, **kwargs):
        # Retrieve the Text object using the unique_id or create new 
        # if it doesn't exist creater it 
        text, created = Text.objects.get_or_create(unique_id=unique_id, created_by=request.user)
        if created:
            text.save()
    
        # Get original_text and url from the request body
        original_text = request.data.get('original_text')
        url = request.data.get('URL')

        # Check if neither original_text nor url is provided
        if not original_text and not url:
            return Response({"error": "Either original_text or url field is required"}, status=status.HTTP_400_BAD_REQUEST)

        # If original_text is provided, use it
        if original_text:
            text_to_rephrase = original_text
        # If url is provided, scrape text from the website
        elif url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extract text from HTML content
                text_to_rephrase = soup.get_text(separator=' ')
                # Remove unnecessary whitespace and newlines
                text_to_rephrase = ' '.join(text_to_rephrase.split())
                
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Rephrase the text_to_rephrase 
        rephrased_text = rephrase(text_to_rephrase)

        # Update the original_text and rephrased_text fields in the Text object
        text.original_text = text_to_rephrase
        text.rephrased_text = rephrased_text
        text.save()

        # Serialize the updated Text object
        serializer = TextSerializer(text)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TextDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Text.objects.all()
    serializer_class = TextSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'unique_id'  # Specify the lookup field as unique_id

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Return a response which includes both the user and group information
        return Response(serializer.data)
    

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TextRepharseImagesView(APIView):
    serializer_class = TextRepharseImageSerializer

    def get_queryset(self):
        unique_id = self.kwargs.get('unique_id')
        return TextRepharseImage.objects.filter(text__unique_id=unique_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def get_text_instance(self, unique_id):
        try:
            return Text.objects.get(unique_id=unique_id)
        except Text.DoesNotExist:
            raise NotFound(detail="Text not found")
        
    def get(self, request, unique_id):
        # Retrieve all images associated with the text
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    def post(self, request, unique_id):
        text = self.get_text_instance(unique_id)
        serializer = TextRepharseImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(text=text)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, unique_id):
        text = self.get_text_instance(unique_id)
        text.rephrased_images.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class TextRepharseImageDetailView(APIView):
    def get(self, request, unique_id, image_id):
        # Get the TextRepharseImage object
        text_image = get_object_or_404(TextRepharseImage, text__unique_id=unique_id, id=image_id)
        # Serialize the object
        serializer = TextRepharseImageSerializer(text_image)
        return Response(serializer.data)
 
    def patch(self, request, unique_id, image_id):
        # Get the TextRepharseImage object
        text_image = get_object_or_404(TextRepharseImage, text__unique_id=unique_id, id=image_id)
        # Serialize the object with the updated data, but allow partial updates
        serializer = TextRepharseImageSerializer(text_image, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, unique_id, image_id):
        # Get the TextRepharseImage object
        text_image = get_object_or_404(TextRepharseImage, text__unique_id=unique_id, id=image_id)
        # Delete the object
        text_image.delete()
        return Response({ "message": "Image deleted successfully" } , status=status.HTTP_204_NO_CONTENT)
