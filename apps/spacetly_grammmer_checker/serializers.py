from rest_framework import serializers
from .models import Document, DocumentImage, DocumentFile

class DocumentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentImage
        fields = ['id','image', 'alt_text', 'created_at', 'updated_at']

class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = ['id','file', 'uploaded_at']

class DocumentSerializer(serializers.ModelSerializer):
    document_images = DocumentImageSerializer(many=True, read_only=True)
    document_files = DocumentFileSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = ['unique_id', 'title', 'content', 'corrected_text','mistakes', 'created_at', 'updated_at', 'document_images', 'document_files']
