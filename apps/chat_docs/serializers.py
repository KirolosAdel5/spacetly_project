from rest_framework import serializers
from .models import Document, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'document', 'content', 'created_at', 'is_from_user', 'in_reply_to')

class DocumentSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Document
        fields = ('id', 'user', 'file', 'cover', 'title', 'created_at', 'updated_at', 'favourite', 'archive', 'messages')
        
        extra_kwargs = {
            'user': {'read_only': True}, 
            'messages': {'read_only': True},
            'cover': {'read_only': True},
            'file': {'required': True},
            'title': {'required': False},
        }

