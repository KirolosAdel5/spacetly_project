from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Avg
from django.contrib.postgres.fields import JSONField
import uuid

from django.contrib.auth import get_user_model
User = get_user_model()


class Category(MPTTModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        verbose_name=_("Category Name"),
        help_text=_("Required and unique"),
        max_length=255,
        unique=True,
    )    
    slug = models.SlugField(unique=True,verbose_name=_("Category safe URL"), max_length=255)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def parent_name(self, obj):
        return obj.parent.name if obj.parent else None

    parent_name.short_description = 'Parent Category'
    def get_parent(self):
        try:
            # Assuming there's a ForeignKey field named 'parent' in your Category model
            return self.parent
        except Category.DoesNotExist:
            return None

class TemplateType(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class TemplateSpecification(models.Model):
    name = models.CharField(max_length=100)
    template_type = models.ForeignKey(TemplateType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class Template(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = TreeForeignKey(Category, on_delete=models.CASCADE)
    template_type = models.ForeignKey(TemplateType, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    icon = models.ImageField(upload_to='template_icons', null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
class TemplateSpecificationField(models.Model):
    TEXT = 'text'
    IMAGE = 'image'
    FILE = 'file'
    FIELD_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
        (FILE, 'File'),
    ]
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='specification_values')
    specification = models.ForeignKey(TemplateSpecification, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    is_required = models.BooleanField(default=False)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default=TEXT)

    def __str__(self):
        return self.name

class FavoriteTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.template.name}"

#user tamplate 
class UserTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    
    input_data = models.JSONField()  # Store user's input data as JSON
    output_data = models.TextField()  # Store the output of executing the template
    
    language = models.CharField(max_length=100)  # Common field: Language
    target_audience = models.CharField(max_length=100)  # Common field: Target Audience
    num_of_results = models.IntegerField(default=10)  # Common field: Number of Results
    tone_of_voice = models.CharField(max_length=100)  # Common field: Tone of Voice

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s {self.template.title} Template"
