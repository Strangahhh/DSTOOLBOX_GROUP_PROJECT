from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid
import numpy as np

class Event(models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Changed field
    name = models.CharField(max_length=255, db_index=True)
    location = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_events')  # Best practice
    staff_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='staffed_events')  # Best practice

    def __str__(self):
        return self.name

def event_image_upload_to(instance, filename):
    return 'event_{0}/{1}'.format(instance.event.event_id, filename)

class Image(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=event_image_upload_to)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} of Event: {self.event.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_cameraman = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
class FaceEncoding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True) 
    encoded = models.TextField()
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='faces') 

    def save(self, *args, **kwargs):
        if isinstance(self.encoded, np.ndarray):
            self.encoded = self.encoded.tolist()  
        super().save(*args, **kwargs)
