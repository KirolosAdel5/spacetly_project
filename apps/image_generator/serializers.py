from rest_framework import serializers
from .models import Image_Gene


class ImageGeneSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = Image_Gene
        fields = '__all__'
        extra_kwargs = {'prompt': {'required': True},
                        'style': {'required': True},
                        'created_by': {'read_only': True},
                        
                        }
        