from rest_framework import serializers
from .models import (
    Category, 
    Template, 
    TemplateSpecification, 
    TemplateSpecificationField, 
    TemplateType, 
    FavoriteTemplate,
    UserTemplate,
    )


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
    class Meta:
        model = TemplateSpecificationField
        fields = '__all__'

class TemplateSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Template
        fields = '__all__'
        
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
    class Meta:
        model = UserTemplate
        fields = '__all__'
        #not reuried 
        read_only_fields = ['user', 'template']

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

