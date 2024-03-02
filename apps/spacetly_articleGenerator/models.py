from django.db import models
from django.utils.text import slugify
from uuid import uuid4
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone

from django.db import models

from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth import get_user_model
User = get_user_model()


class Keyword(models.Model):
    topic = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    num_keywords = models.IntegerField(default=10)  # Default to 10 keyword

    def __str__(self):
        return self.subject

class Title(models.Model):
    topic = models.CharField(max_length=100)
    keywords = models.ManyToManyField(Keyword)
    num_titles = models.IntegerField()
    tone_of_voice = models.CharField(max_length=100)
    language = models.CharField(max_length=50)

    def __str__(self):
        return self.subject

class Image(models.Model):
    size = models.CharField(max_length=50)
    num_results = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.description[:50] + "..."

class Subheading(MPTTModel):
    title = models.CharField(max_length=100)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    keywords = models.ManyToManyField(Keyword)
    tone_of_voice = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    num_keywords = models.IntegerField()

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title

class Article(models.Model):
    main_title = models.CharField(max_length=100)
    subheadings = models.ManyToManyField(Subheading)
    selected_keywords = models.ManyToManyField(Keyword)
    tone_of_voice = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=255, help_text="Unique URL path to access this article. Generated automatically based on the title.")
    unique_id = models.UUIDField(default=uuid4, editable=False, unique=True, help_text="Unique identifier for this article, generated automatically.")
    created_at = models.DateTimeField(default=timezone.now, editable=False, help_text="Date and time when this article was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when this article was last updated.")

    def save(self, *args, **kwargs):
        # Generate slug when saving if it's not provided
        if not self.slug:
            self.slug = slugify(self.main_title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.main_title

    class Meta:
        ordering = ['-created_at']  # Display articles in descending order of creation time
        verbose_name = "Article"
        verbose_name_plural = "Articles"

class SavedArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'article']
