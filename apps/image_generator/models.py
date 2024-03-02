from django.db import models
from django.conf import settings
import uuid
import os
class Image_Gene(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    num_of_image = models.IntegerField(default=1)
    prompt = models.TextField()
    style = models.CharField(max_length=50)
    resolution = models.CharField(max_length=50)
    
    image_paths = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return self.username

    def delete(self, *args, **kwargs):
        # Remove image files from media directory
        for image_id, file_path in self.image_paths.items():
            image_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(image_file_path):
                os.remove(image_file_path)
        super().delete(*args, **kwargs)