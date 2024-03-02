from django.db import models
from django.conf import settings
import secrets

def generate_secure_random_id():
    min_value = 10 ** 10  # Minimum value of the range (inclusive)
    max_value = 10 ** 11 - 1  # Maximum value of the range (exclusive)
    return secrets.randbelow(max_value - min_value) + min_value

class Conversation(models.Model):
    """
    Conversation model representing a chat conversation.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('ended', 'Ended'),
    ]
    
    AI_MODEL_CHOICES = [
        ('ChatGPT', 'ChatGPT (Free)'),
        ('GPT4', 'GPT4 (Paid)'),
        ('Google PalM 2', 'Google PalM 2 (Paid)'),
        # Add onther to image generator
        ('ImageGenerator', 'ImageGenerator'),
    ]

    id = models.BigIntegerField(primary_key=True, default=generate_secure_random_id, editable=False)
    title = models.CharField(max_length=255, default="Empty")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favourite = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    ai_model = models.CharField(max_length=50, choices=AI_MODEL_CHOICES, default='Google PalM 2')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Conversation {self.title} - {self.user.username}"

class Message(models.Model):
    """
    Message model representing a message within a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)  # Field for image upload
    file = models.FileField(upload_to='files/', null=True, blank=True)      # Field for file upload
    url = models.URLField(null=True, blank=True)                            # Field for URL

    created_at = models.DateTimeField(auto_now_add=True)
    is_from_user = models.BooleanField(default=True)
    in_reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')

  
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message {self.id} - {self.conversation}"