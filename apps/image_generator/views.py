from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.
from .models import Image_Gene 
from .serializers import ImageGeneSerializer
from .tasks import image_genrate
from rest_framework.permissions import IsAuthenticated  
import uuid 
from django.shortcuts import get_object_or_404

class ImageGeneCreateView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        serializer = ImageGeneSerializer(data=request.data)
        if serializer.is_valid():
            # Create a UUID for the id field
            instance_id = uuid.uuid4()
            # Set the id field of the instance
            serializer.validated_data['id'] = instance_id
            # Save the instance
            image_gene_instance = serializer.save(created_by=request.user)
            # Assuming 'topic', 'style', 'num_of_images', and 'resolution' are provided in the request
            images = image_genrate(image_gene_instance.prompt)
            # Construct dictionary with UUIDs as keys and URLs as values
            image_paths_dict = images
            # Assign the image_paths dictionary to the image_paths field of the instance
            image_gene_instance.image_paths = image_paths_dict
            image_gene_instance.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)

class RetrieveAllImagesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        images = Image_Gene.objects.filter(created_by=request.user)
        serializer = ImageGeneSerializer(images, many=True)
        return Response(serializer.data)

class RetrieveSpecificImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, image_id):
        image = get_object_or_404(Image_Gene, id=image_id, created_by=request.user)
        serializer = ImageGeneSerializer(image)
        return Response(serializer.data)
    
class RemoveImageView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, image_id):
        image = get_object_or_404(Image_Gene, id=image_id , created_by=request.user) 
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class RetrieveSingleImageView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, image_id, pk):
#         # Retrieve the image instance using the UUID
#         image = get_object_or_404(Image_Gene, id=image_id)
        
#         # Get the image paths dictionary
#         image_paths = image.image_paths
        
#         # Get the URL corresponding to the image UUID
#         image_url = image_paths.get(str(pk))
        
#         if image_url:
#             return Response({"image_url": image_url})
#         else:
#             return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

# class DeleteSingleImageView(APIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, image_id, pk):
#         # Retrieve the image instance using the UUID
#         image = get_object_or_404(Image_Gene, id=image_id)
        
#         # Get the image paths dictionary
#         image_paths = image.image_paths
        
#         # Remove the entry corresponding to the image UUID
#         if str(pk) in image_paths:
#             del image_paths[str(pk)]
#             # Save the updated image instance
#             image.save()
#             return Response({"message": "Image removed successfully"}, status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

