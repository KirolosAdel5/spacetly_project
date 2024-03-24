from rest_framework import generics,viewsets,permissions,pagination ,filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from .models import Category, Template, TemplateSpecification, TemplateSpecificationField, TemplateType , UserTemplate,FavoriteTemplate
from ..ai_document_editor.models import Document
from .serializers import CategorySerializer, TemplateSerializer, TemplateTypeSerializer, TemplateSpecificationSerializer, TemplateSpecificationFieldSerializer , UserTemplateSerializer , FavoriteTemplateSerializer
from .permission import IsAdminOrReadOnly
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from .tasks import do_prompt
from rest_framework.permissions import IsAuthenticated
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
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category','category__name','category__slug']  # Specify fields for filtering
    search_fields = ['title', 'description']  # Specify fields for searching
    ordering_fields = ['created_at', 'title']  # Specify fields for ordering

    def get_queryset(self):
        queryset = super().get_queryset()
        # Perform any additional filtering or custom queryset manipulation here if needed
        return queryset
     

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
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return FavoriteTemplate.objects.filter(user=user)
    def create(self, request, *args, **kwargs):
        # Extract template UUID from the URL kwargs
        template_id = self.kwargs.get('template_id')
        # Retrieve template instance or raise a 404 error if not found
        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the template is already favorited by the user
        favorite_exists = FavoriteTemplate.objects.filter(user=request.user, template=template).exists()

        if favorite_exists:
            # If the template is already favorited, remove it from favorites
            FavoriteTemplate.objects.filter(user=request.user, template=template).delete()
            return Response({'message': 'Template removed from favorites'}, status=status.HTTP_200_OK)
        else:
            # If the template is not favorited, add it to favorites
            favorite_template = FavoriteTemplate(user=request.user, template=template)
            favorite_template.save()
            return Response({'message': 'Template added to favorites'}, status=status.HTTP_201_CREATED)

class TemplateFieldsAPIView(APIView):
    def get(self, request, template_id):
        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)

        fields = TemplateSpecificationField.objects.filter(template=template)
        serializer = TemplateSpecificationFieldSerializer(fields, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LastTemplatesPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10

class UserTemplateListCreateAPIView(generics.ListAPIView):
    queryset = UserTemplate.objects.all()
    serializer_class = UserTemplateSerializer
    pagination_class = LastTemplatesPagination
    def get_queryset(self):
        user = self.request.user
        return UserTemplate.objects.filter(user=user)
    
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
        input_data = {}
        for field in specification_fields:
            if field.is_required:
                field_name = field.specification.name
                if field_name not in request.data:
                    raise ValidationError({field_name: ["This field is required."]})
                input_data[field_name] = request.data[field_name]
            
        template_type = template_instance.template_type
        prompt = f"""please {template_type} with this info :\n"""
        for key, value in input_data.items():
            prompt += f"{key}: {value}\n"
        prompt += f"""
                Language: {request.data.get('language','en')}
                Target Audience: {request.data.get('target_audience','everyone')}
                Number of Results: {request.data.get('number_of_results',5)}
                Tone of Voice:{request.data.get('tone_of_voice','professional')}    
                
                i need from  you make {template_instance.description}
                make sure that the result be in markdown format
                """    
        #send previous prompt to openai
        res = do_prompt(prompt)['text']
        
        document = Document.objects.create(content=res,user=request.user)
        
        user_template = UserTemplate.objects.create(
            user=request.user, 
            content=res,
            template=template_instance,                                         
            input_data=input_data,
            language = request.data.get('language','en'),
            target_audience=request.data.get('target_audience','everyone'),
            num_of_results = request.data.get('number_of_results',5),
            tone_of_voice = request.data.get('tone_of_voice','professional'),
            document=document

            )
        

        return Response(UserTemplateSerializer(user_template).data, status=status.HTTP_201_CREATED)

class UserTemplateRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserTemplate.objects.all()
    serializer_class = UserTemplateSerializer
    premission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return UserTemplate.objects.filter(user=user)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        document_id = instance.document_id
        document = Document.objects.get(id=document_id)
        if 'content' in request.data:
            new_content = request.data.get('content')
            # Update the associated document's content
            document.content = new_content
            document.save()
            instance.content = new_content
            instance.save()
        
        if 'title' in request.data:
            new_title = request.data.get('title')
            # Update the associated document's title
            document.title = new_title
            document.save()
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            self.perform_destroy(instance)
            return Response({"message": "template was successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "template not found."}, status=status.HTTP_404_NOT_FOUND)
