from rest_framework import serializers
from .models import (
    Category, 
    Template, 
    TemplateSpecification, 
    TemplateSpecificationField, 
    TemplateType, 
    UserTemplate,
    FavoriteTemplate,
    )

from .utils import time_since
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','slug','is_active']


class TemplateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateType
        fields = '__all__'


class TemplateSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateSpecification
        fields = '__all__'


class TemplateSpecificationFieldSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    title = serializers.CharField(source='name')  # Map 'name' field to 'title'
    class Meta:
        model = TemplateSpecificationField
        fields = ['id', 'name', 'title', 'description', 'is_required', 'field_type','template']
        
    def get_name(self, obj):
        return obj.specification.name

class TemplateSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    category__name = serializers.SerializerMethodField()
    class Meta:
        model = Template
        fields = ['id', 'title', 'description', 'icon','slug', 'category','category__name', 'created_by', 'is_active','template_type']

    def get_category__name(self, obj):
        return obj.category.name
        
    def create(self, validated_data):
        # Get the authenticated user from the request if available
        user = self.context['request'].user if 'request' in self.context else None

        # Add the authenticated user to the validated data if available
        if user:
            validated_data['created_by'] = user

        # Create and return the new instance
        return super().create(validated_data)
class FavoriteTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteTemplate
        fields = '__all__'

class UserTemplateSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = UserTemplate
        fields = '__all__'
        #not reuried 
        read_only_fields = ['user', 'template', 'input_data','content']
        

    def create(self, validated_data):
        # Automatically set the user to the currently authenticated user
        validated_data['user'] = self.context['request'].user

        # Retrieve the template ID from the URL
        template_id = self.context['view'].kwargs.get('template_id')
        
        # If template_id is not provided or not valid, raise a validation error
        if not template_id:
            raise serializers.ValidationError("Template ID is required.")
        
        # Retrieve the template instance or raise a 404 error if not found
        template_instance = get_object_or_404(Template, id=template_id)
        
        # Set the template field
        validated_data['template'] = template_instance

        # Perform the default create behavior
        return super().create(validated_data)

    def get_created_at(self, obj):
        return time_since(obj.created_at)

    def get_updated_at(self, obj):
        return time_since(obj.updated_at)
    
    def get_title(self, obj):
        if obj.document : 
            return obj.document.title
        return None
    
