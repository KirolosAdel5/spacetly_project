# serializers.py
from rest_framework import serializers
from .models import MutqinAssistant
from .utils import time_since

class MutqinAssistantSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = MutqinAssistant
        fields = ['id', 'document','title','template', 'question','language', 'content', 'user', 'created_at', 'updated_at']
        
    def get_created_at(self, obj):
        return time_since(obj.created_at)

    def get_updated_at(self, obj):
        return time_since(obj.updated_at)
    
    def get_title(self, obj):
        if obj.document : 
            return obj.document.title
        return None
    