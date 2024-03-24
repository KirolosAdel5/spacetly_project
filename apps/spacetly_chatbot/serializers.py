from rest_framework import serializers

from .models import Conversation, Message
from .utils import time_since
import json


class MessageSerializer(serializers.ModelSerializer):
    """
    Message serializer.
    """
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'reloaded_message' in representation and representation['reloaded_message']:
            representation['reloaded_message'] = json.loads(representation['reloaded_message'])
        return representation
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'reloaded_message', 'content', 'is_from_user', 'in_reply_to', 'created_at', ]


class ConversationSerializer(serializers.ModelSerializer):
    """
    Conversation serializer.
    """
    messages = MessageSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'ai_model','favourite', 'archive', 'created_at', 'messages']

    def get_created_at(self, obj):
        return time_since(obj.created_at)
