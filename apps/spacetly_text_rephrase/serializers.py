from rest_framework import serializers
from .models import Text, TextRepharseImage

class TextRepharseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextRepharseImage
        fields = '__all__'
        extra_kwargs = {
            'image': {'required': True},
            'text': {'required': False},  
        }

class TextSerializer(serializers.ModelSerializer):
    rephrased_images = TextRepharseImageSerializer(many=True, read_only=True)

    class Meta:
        model = Text
        fields = ['unique_id','title','original_text', 'rephrased_text', 'created_at','updated_at', 'rephrased_images']
