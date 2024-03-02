from rest_framework import generics,viewsets,permissions
from .models import Category, Template, TemplateSpecification, TemplateSpecificationField, TemplateType, FavoriteTemplate , UserTemplate
from .serializers import CategorySerializer, TemplateSerializer, TemplateTypeSerializer, TemplateSpecificationSerializer, TemplateSpecificationFieldSerializer, FavoriteTemplateSerializer , UserTemplateSerializer
from .permission import IsAdminOrReadOnly
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]  # Allow authenticated users to create, everyone to read
class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]  # Allow only admins to update and delete


class TemplateTypeListCreateAPIView(generics.ListCreateAPIView):
    queryset = TemplateType.objects.all()
    serializer_class = TemplateTypeSerializer
    permission_classes = [permissions.IsAdminUser] 

class TemplateTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TemplateType.objects.all()
    serializer_class = TemplateTypeSerializer
    permission_classes = [permissions.IsAdminUser] 

class TemplateSpecificationListCreateAPIView(generics.ListCreateAPIView):
    queryset = TemplateSpecification.objects.all()
    serializer_class = TemplateSpecificationSerializer
    permission_classes = [permissions.IsAdminUser] 


class TemplateSpecificationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TemplateSpecification.objects.all()
    serializer_class = TemplateSpecificationSerializer
    permission_classes = [permissions.IsAdminUser] 

class TemplateSpecificationListByTypeView(generics.ListAPIView):
    serializer_class = TemplateSpecificationSerializer
    permission_classes = [permissions.IsAdminUser] 

    def get_queryset(self):
        template_type_id = self.kwargs['template_type_id']
        try:
            # Retrieve template specifications by template type ID
            return TemplateSpecification.objects.filter(template_type=template_type_id)
        except TemplateSpecification.DoesNotExist:
            raise Http404("Template specifications not found for the given template type ID.")

class TemplateListCreateAPIView(generics.ListCreateAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAdminOrReadOnly] 

class TemplateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAdminOrReadOnly]


class TemplateSpecificationFieldListCreateAPIView(generics.ListCreateAPIView):
    queryset = TemplateSpecificationField.objects.all()
    serializer_class = TemplateSpecificationFieldSerializer

class TemplateSpecificationFieldRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TemplateSpecificationField.objects.all()
    serializer_class = TemplateSpecificationFieldSerializer

class TemplateSpecificationFieldByTemplateAPIView(generics.ListAPIView):
    serializer_class = TemplateSpecificationFieldSerializer

    def get_queryset(self):
        template_id = self.kwargs.get('template_id')
        return TemplateSpecificationField.objects.filter(template=template_id)
    
class FavoriteTemplateListCreateAPIView(generics.ListCreateAPIView):
    queryset = FavoriteTemplate.objects.all()
    serializer_class = FavoriteTemplateSerializer

class UserTemplateCreateAPIView(generics.CreateAPIView):
    queryset = UserTemplate.objects.all()
    serializer_class = UserTemplateSerializer
    def create(self, request, *args, **kwargs):
        # Extract template UUID from the URL kwargs
        template_id = self.kwargs['template_id']
        # Retrieve template instance
        template_instance = get_object_or_404(Template, id=template_id)
        # Access template specification fields and mark required fields as required
        specification_fields = TemplateSpecificationField.objects.filter(template=template_instance)
        for field in specification_fields:
            if field.is_required:
                field_name = field.name
                if field_name not in request.data:
                    raise ValidationError({field_name: ["This field is required."]})

        # Perform the default create behavior
        return super().create(request, *args, **kwargs)

class UserTemplateRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = UserTemplate.objects.all()
    serializer_class = UserTemplateSerializer
    lookup_field = 'id'