from django.db import models
from django.conf import settings
import uuid
import os
class Image_Gene(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # num_of_image = models.IntegerField(default=1)
    prompt = models.TextField()
    # style = models.CharField(max_length=50)
    # resolution = models.CharField(max_length=50)
    
    image_paths = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return self.username

    def delete(self, *args, **kwargs):
        try:
                
            image_relative_path = self.image_paths.split('/media/', 1)[-1]
            
            # Construct full file path relative to MEDIA_ROOT
            image_file_path = os.path.join(settings.MEDIA_ROOT, image_relative_path)

            if os.path.exists(image_file_path):
                os.remove(image_file_path)
            super().delete(*args, **kwargs)
        
        except Exception as e:
            super().delete(*args, **kwargs)
