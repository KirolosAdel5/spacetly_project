from rest_framework import serializers
from .models import Articles
from .utils import time_since


# Article
class AllArticlesSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    class Meta:
        model = Articles
        fields = ['id', 'user', 'created_at', 'updated_at','title','subtitles','keywords','language','tone_of_voice','content']
    
    def get_created_at(self, obj):
        return time_since(obj.created_at)

    def get_updated_at(self, obj):
        return time_since(obj.updated_at)

