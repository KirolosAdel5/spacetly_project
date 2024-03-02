from rest_framework import serializers
from .models import Document, DocumentImage
from .utils import time_since
class DocumentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentImage
        fields = ['id', 'image']

class DocumentSerializer(serializers.ModelSerializer):
    images = DocumentImageSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'user', 'images']
        #user read only
        extra_kwargs = {
            'user': {'read_only': True}
        }
        
    def get_created_at(self, obj):
        return time_since(obj.created_at)

    def get_updated_at(self, obj):
        return time_since(obj.updated_at)