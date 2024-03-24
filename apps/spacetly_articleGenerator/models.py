import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

User = get_user_model()

class Articles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="Unique identifier for this article, generated automatically.")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False, help_text="Date and time when this article was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when this article was last updated.")
    
    title = models.CharField(max_length=255, blank=True, help_text="Article title")
    
    subtitles = models.JSONField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    language = models.CharField(max_length=10, blank=True, null=True)
    tone_of_voice = models.CharField(max_length=20, blank=True, null=True)
      
    content = models.TextField(blank=True, help_text="Article content")

    # step0 = models.JSONField(default=dict, help_text="Step 0 content")
    # step1 = models.JSONField(default=dict, help_text="Step 1 content")
    # step2 = models.JSONField(default=dict, help_text="Step 2 content")
    # step3 = models.JSONField(default=dict, help_text="Step 3 content")
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-updated_at']
        