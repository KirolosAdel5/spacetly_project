from django.db import models
from uuid import uuid4
from django.utils import timezone
from django.utils.translation import gettext as _

from django.contrib.auth import get_user_model
User = get_user_model()


class Text(models.Model):
    """
    The Text table
    table contain the original text and the rephrased text. 
    """
    
    title = models.CharField(max_length=100, default="Untitled")
    original_text = models.TextField(blank=True, null=True)
    rephrased_text = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unique_id = models.UUIDField(default=uuid4, editable=False, unique=True, help_text="Unique identifier for this text repharse, generated automatically.")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.title and self.original_text:
            # Set title to the first letters of the original_text
            self.title = self.original_text[:50]
        super().save(*args, **kwargs)
    
class TextRepharseImage(models.Model):
    """
    The Text Rephrase Image table.
    """

    text = models.ForeignKey(Text, on_delete=models.CASCADE, related_name="rephrased_images")
    image = models.ImageField(
        verbose_name=_("image"),
        help_text=_("Upload an image related to the rephrased text"),
        upload_to="images/text_rephrased_images/",
    )
    alt_text = models.CharField(
        verbose_name=_("Alternative text"),
        help_text=_("Please add alternative text"),
        max_length=255,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Text Rephrase Image")
        verbose_name_plural = _("Text Rephrase Images")
