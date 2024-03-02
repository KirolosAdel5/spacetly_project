from django.db import models
import uuid
from django.contrib.auth import get_user_model
User = get_user_model()

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, default="New Document")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_document_set')

    def __str__(self):
        return self.title

class DocumentImage(models.Model):
    document = models.ForeignKey(Document, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ai_document_images/')

    def __str__(self):
        return f"Image for {self.document.title}"
