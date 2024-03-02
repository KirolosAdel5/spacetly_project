from django.db import models
from uuid import uuid4
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.validators import FileExtensionValidator

from django.contrib.auth import get_user_model
User = get_user_model()


class Document(models.Model):
    title = models.CharField(max_length=100, default="New Document")
    content = models.TextField( blank=True, null=True)
    corrected_text = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unique_id = models.UUIDField(default=uuid4, editable=False, unique=True, help_text="Unique identifier for this text repharse, generated automatically.")

    mistakes = models.JSONField(blank=True, null=True)  # Field to store mistakes

    def __str__(self):
        return self.title

class DocumentImage(models.Model):
    """
    The Document Image table.
    """

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="document_images")
    image = models.ImageField(
        verbose_name=_("Image"),
        help_text=_("Upload an image related to the document"),
        upload_to="images/grammer_checker/",
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
        verbose_name = _("Document Image")
        verbose_name_plural = _("Document Images")

class DocumentFile(models.Model):
    """
    The Document File table.
    """

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="document_files")
    file = models.FileField(
        verbose_name=_("File"),
        help_text=_("Upload a document file (Word or PDF)"),
        upload_to="files/grammer_checker/",
        validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx', 'pdf'])],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Document File")
        verbose_name_plural = _("Document Files")
