from django.db import models
import uuid
from django.contrib.auth import get_user_model
User = get_user_model()

class MutqinAssistant(models.Model):
    # uuid id 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey('ai_document_editor.Document', on_delete=models.CASCADE)
    
    template = models.CharField(max_length=100,null=True)
    question = models.TextField()
    language = models.CharField(max_length=100,default="en")
    
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mutqin_assistant_set')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']