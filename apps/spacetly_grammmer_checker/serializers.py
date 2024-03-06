from rest_framework import serializers
from .models import Document, DocumentImage, DocumentFile
from .utils import time_since
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
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['unique_id', 'title', 'content', 'corrected_text','mistakes', 'created_at', 'updated_at', 'document_images', 'document_files']
    
    def get_created_at(self, obj):
        return time_since(obj.created_at)

    def get_updated_at(self, obj):
        return time_since(obj.updated_at)

class RichTextInputSerializer(serializers.Serializer):
    rich_text = serializers.CharField()