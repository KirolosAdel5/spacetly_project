from rest_framework import generics, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
# from celery.result import AsyncResult
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter
import os
from django.conf import settings
from .models import Document, Message
from .serializers import MessageSerializer, DocumentSerializer
from .tasks import LangchainGemeni
User = get_user_model()

# Create your views here.
#hello world api view 
class DocumentsListCreate(generics.ListCreateAPIView):
    """
    List and create Documents.
    """
    serializer_class = DocumentSerializer
    filter_backends = [ SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by('created_at')

    def perform_create(self, serializer):
        uploaded_file_name = self.request.data.get('file').name
        serializer.save(user=self.request.user, title=uploaded_file_name)


    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        deleted_count, _ = queryset.delete()
        if deleted_count > 0:
            return Response({"message": "All Documents were successfully removed."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No Documents to remove."}, status=status.HTTP_204_NO_CONTENT)
    
class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete a specific Document.
    """
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        document = self.get_object()
        if document.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Delete the main file
        if document.file:
            file_relative_path = document.file.path.split('/media/', 1)[-1]
            
            # Construct full file path relative to MEDIA_ROOT
            file_path = os.path.join(settings.MEDIA_ROOT, file_relative_path)

     
            # file_path = document.file.path
            
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete the cover image if it exists
        if document.cover:
            cover_relative_path = document.file.path.split('/media/', 1)[-1]
            
            # Construct full file path relative to MEDIA_ROOT
            cover_path = os.path.join(settings.MEDIA_ROOT, cover_relative_path)

            # cover_path = document.cover.path
            if os.path.exists(cover_path):
                os.remove(cover_path)

        # Call the superclass delete method to delete the document from the database
        return super().delete(request, *args, **kwargs)



class DocumentArchive(APIView):
    """
    Archive a document.
    """

    def patch(self, request, pk):
        document_instance  = get_object_or_404(Document, id=pk, user=request.user)
        if document_instance .archive:
            document_instance .archive = False
            document_instance .save()
            return Response({"message": "remove from archive"}, status=status.HTTP_200_OK)
        else:
            document_instance .archive = True
            document_instance .save()
            return Response({"message": "add to archive"}, status=status.HTTP_200_OK)


class DocumentFavourite(APIView):
    """
    Favourite a document.
    """

    def patch(self, request, pk):
        document_instance  = get_object_or_404(Document, id=pk, user=request.user)
        if document_instance .favourite:
            document_instance .favourite = False
            document_instance .save()
            return Response({"message": "remove from favourite"}, status=status.HTTP_200_OK)
        else:
            document_instance .favourite = True
            document_instance .save()
            return Response({"message": "add to favourite"}, status=status.HTTP_200_OK)

class LastMessagesPagination(LimitOffsetPagination):
    """
    Pagination class for last messages.
    """
    default_limit = 10
    max_limit = 10

class MessageList(generics.ListAPIView):
    """
    List messages in a document.
    """
    serializer_class = MessageSerializer
    pagination_class = LastMessagesPagination

    def get_queryset(self):
        document = get_object_or_404(Document, id=self.kwargs['document_id'], user=self.request.user)
        return Message.objects.filter(document=document).select_related('document')

# Create a message in a conversation
class MessageCreate(generics.CreateAPIView):
    """
    Create a message in a  document.
    """
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        document = get_object_or_404(Document, id=self.kwargs['document_id'], user=self.request.user)
        serializer.save(document=document, is_from_user=True)

        # Retrieve the last 10 messages from the document
        messages = Message.objects.filter(document=document).order_by('-created_at')[:10][::-1]

        # Build the list of dictionaries containing the message data
        message_list = []
        for msg in messages:
            if msg.is_from_user:
                message_list.append({"role": "user", "content": msg.content})
            else:
                message_list.append({"role": "assistant", "content": msg.content})
        
        model = LangchainGemeni(os.getenv("GOOGLE_API_KEY"), temperature=0.3)
        
        file_relative_path = document.file.path.split('/media/', 1)[-1]
            
        # Construct full file path relative to MEDIA_ROOT
        file_path = os.path.join(settings.MEDIA_ROOT, file_relative_path)

        # Convert your enemies... er, PDF pages into vectors
        model.AIEmbeddingsPdfPages2Vector(file_path)

        # Summon your trusty Question-Answering guardian
        qa_client = model.BuildQA(return_source_documents=True)

        qa_model = qa_client({
            'query': message_list[-1]["content"]
        })
        response =  qa_model['result']
        
        # raw_text = get_pdf_text(["/django/public/media/chat-ai-documents/Eyad_Aiman.pdf" ])
        # text_chunks = get_text_chunks(raw_text)
        # get_vector_store(text_chunks)

        # response =  user_input(message_list[-1]["content"])["output_text"]
    
        return response, document.id, messages[0].id

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response, document_id, last_user_message_id = self.perform_create(serializer)

        try:
            # Store chat response as a message
            message = Message(
                document_id=document_id,
                content=response,
                is_from_user=False,
                in_reply_to_id=last_user_message_id
            )
            message.save()
 

            headers = self.get_success_headers(serializer.data)
            
            return Response(
                {
                    "response": response,
                    "document_id": document_id,
                    "message_id": message.id
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )

        except ObjectDoesNotExist as e:
            error = f"Document with id {document_id} does not exist"
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            error_msg = str(e)
            error = f"Failed to save chat response as a message: {error_msg}"
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)



