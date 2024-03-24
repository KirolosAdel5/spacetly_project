import uuid
from django.db import models
from django.contrib.auth.models import User  # Import the User model
from django.core.validators import  FileExtensionValidator
from django.db import models
from django.conf import settings
import secrets
from django.core.exceptions import ValidationError

def validate_file_size(value):
    filesize = value.size
    
    if filesize > 20 * 1024 * 1024:  # 20 MB limit
        raise ValidationError("The maximum file size that can be uploaded is 20MB")


class Document(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('ended', 'Ended'),
    ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_ai_documents')
    file = models.FileField(upload_to='chat-ai-documents/', validators=[validate_file_size, FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])])
    
    cover = models.ImageField(upload_to='chat-ai-documents-cover/', blank=True, null=True)  # Cover image field

    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favourite = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['created_at']

class Message(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_from_user = models.BooleanField(default=True)  
    in_reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Query about {self.document.title} - {self.created_at}"
