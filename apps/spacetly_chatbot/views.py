from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
# from celery.result import AsyncResult
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
# from .tasks import send_gpt_request, generate_title_request
from .tasks import chat, memory, define_conv_chain , google_gemini, chat_openai_gpt3, chat_openai_gpt4
import json
from django.core.serializers.json import DjangoJSONEncoder

# from .chat_image import image_genrate
User = get_user_model()


class LastMessagesPagination(LimitOffsetPagination):
    """
    Pagination class for last messages.
    """
    default_limit = 10
    max_limit = 10


# List and create conversations
class ConversationListCreate(generics.ListCreateAPIView):
    """
    List and create conversations.
    """
    serializer_class = ConversationSerializer
    filter_backends = [ SearchFilter]
    search_fields = ['title','ai_model']


    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user).order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        deleted_count, _ = queryset.delete()
        if deleted_count > 0:
            return Response({"message": "All conversations were successfully removed."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No conversations to remove."}, status=status.HTTP_204_NO_CONTENT)

# Retrieve, update, and delete a specific conversation
class ConversationDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete a specific conversation.
    """
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        conversation = self.get_object()
        if conversation.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


# Archive a conversation
class ConversationArchive(APIView):
    """
    Archive a conversation.
    """

    def patch(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk, user=request.user)
        if conversation.archive:
            conversation.archive = False
            conversation.save()
            return Response({"message": "remove from archive"}, status=status.HTTP_200_OK)
        else:
            conversation.archive = True
            conversation.save()
            return Response({"message": "add to archive"}, status=status.HTTP_200_OK)


class ConversationFavourite(APIView):
    """
    Favourite a conversation.
    """

    def patch(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk, user=request.user)
        if conversation.favourite:
            conversation.favourite = False
            conversation.save()
            return Response({"message": "remove from favourite"}, status=status.HTTP_200_OK)
        else:
            conversation.favourite = True
            conversation.save()
            return Response({"message": "add to favourite"}, status=status.HTTP_200_OK)


# Delete a conversation
class ConversationDelete(APIView):
    """
    Delete a conversation.
    """

    def delete(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk, user=request.user)
        conversation.delete()
        return Response({"message": "conversation deleted"}, status=status.HTTP_200_OK)


# List messages in a conversation
class MessageList(generics.ListAPIView):
    """
    List messages in a conversation.
    """
    serializer_class = MessageSerializer
    pagination_class = LastMessagesPagination

    def get_queryset(self):
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'], user=self.request.user)
        return Message.objects.filter(conversation=conversation).select_related('conversation')

# Create a message in a conversation
class MessageCreate(generics.CreateAPIView):
    """
    Create a message in a conversation.
    """
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'], user=self.request.user)
        serializer.save(conversation=conversation, is_from_user=True)

        # Retrieve the last 10 messages from the conversation
        messages = Message.objects.filter(conversation=conversation).order_by('-created_at')[:10][::-1]

        # Build the list of dictionaries containing the message data
        message_list = []
        for msg in messages:
            if msg.is_from_user:
                message_list.append({"role": "user", "content": msg.content})
            else:
                message_list.append({"role": "assistant", "content": msg.content})
        
        #check if ai_model in body and if not set it to default
        if 'ai_model' in self.request.data:
            conversation.ai_model = self.request.data['ai_model']
            conversation.save() 
        
        
        if conversation.ai_model == "ChatGPT":
            chat_model = define_conv_chain(memory, chat_openai_gpt3)
        elif conversation.ai_model == "GPT4":
            chat_model = define_conv_chain(memory, chat_openai_gpt4)
        elif conversation.ai_model == "Google PalM 2":
            chat_model = define_conv_chain(memory, google_gemini)
        elif conversation.ai_model == "ImageGenerator":
            # response = image_genrate(message_list[-1]["content"])
            response = "this feature is not yet available"
        else:
            # Default to Google PalM 2 if the provided AI model is invalid
            chat_model = define_conv_chain(memory, google_gemini)
            
        if conversation.ai_model != "ImageGenerator":
            # Call the chat logic function to get a response
            response = chat(chat_model, message_list[-1]["content"])
        
        #Genrate title if fist message in conversition
        conversation = get_object_or_404(Conversation, id=self.kwargs['conversation_id'], user=self.request.user)
        if conversation.title == "Empty":
            title = messages[-1].content
            try:
                conversation.title = title[:30]
            except:
                conversation.title = title
                
            conversation.save()

        
        return response, conversation.id, messages[-1].id

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response, conversation_id, last_user_message_id = self.perform_create(serializer)

        try:
            # Store chat response as a message
            message = Message(
                conversation_id=conversation_id,
                content=response,
                is_from_user=False,
                in_reply_to_id=last_user_message_id
            )
            message.save()
 

            headers = self.get_success_headers(serializer.data)
            
            return Response(
                {
                    "response": response,
                    "conversation_id": conversation_id,
                    "message_id": message.id
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )

        except ObjectDoesNotExist as e:
            error = f"Conversation with id {conversation_id} does not exist"
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            error_msg = str(e)
            error = f"Failed to save chat response as a message: {error_msg}"
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)


class ConversationRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Retrieve View to update or get the title
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    lookup_url_kwarg = 'conversation_id'

    def retrieve(self, request, *args, **kwargs):
        conversation = self.get_object()

        if conversation.title == "Empty":
            messages = Message.objects.filter(conversation=conversation)

            if messages.exists():
                message_list = []
                for msg in messages:
                    if msg.is_from_user:
                        message_list.append({"role": "user", "content": msg.content})
                    else:
                        message_list.append({"role": "assistant", "content": msg.content})

                # task = generate_title_request.apply_async(args=(message_list,))
                # my_title = task.get()
                # # if length of title is greater than 55, truncate it
                # my_title = my_title[:30]
                conversation.title = "my_title"
                conversation.save()
                serializer = self.get_serializer(conversation)
                return Response(serializer.data)
            else:
                return Response({"message": "No messages in conversation."}, status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)

class MessageReloadResponse(APIView):
    def post(self, request, conversation_id, message_id):
        # Fetch the current message
        message = get_object_or_404(Message, id=message_id, conversation_id=conversation_id)
        
        # Fetch the previous message associated with in_reply_to_id
        previous_message = get_object_or_404(Message, id=message.in_reply_to_id, conversation_id=conversation_id)
        
        # Fetch the conversation
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)

        # Retrieve existing reloaded messages if any
        reloaded_messages = json.loads(message.reloaded_message) if message.reloaded_message else []

        # Check the AI model and define the chat model accordingly
        if conversation.ai_model == "ChatGPT":
            chat_model = define_conv_chain(memory, chat_openai_gpt3)
        elif conversation.ai_model == "GPT4":
            chat_model = define_conv_chain(memory, chat_openai_gpt4)
        elif conversation.ai_model == "Google PalM 2":
            chat_model = define_conv_chain(memory, google_gemini)
        elif conversation.ai_model == "ImageGenerator":
            # For ImageGenerator, handle the response differently
            response = "This feature is not yet available"
        else:
            # Default to Google PalM 2 if the provided AI model is invalid
            chat_model = define_conv_chain(memory, google_gemini)
        
        if conversation.ai_model != "ImageGenerator":
            response = chat(chat_model, previous_message.content)

        # Append the new response to the reloaded_messages list
        reloaded_messages.append(response)

        # Update the reloaded_message field of the message object with the updated list
        message.reloaded_message = json.dumps(reloaded_messages)
        message.save()

        return Response({"response": reloaded_messages})        
        

# class GPT3TaskStatus(APIView):
#     """
#     Check the status of a GPT task and return the result if it's ready.
#     """

#     def get(self, request, task_id, *args, **kwargs):
#         task = AsyncResult(task_id)

#         if task.ready():
#             response = task.result
#             return Response({"status": "READY", "response": response})
#         else:
#             return Response({"status": "PENDING"})
