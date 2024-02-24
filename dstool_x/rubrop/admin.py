from django.contrib import admin
from .models import Event, Image, UserProfile, FaceEncoding

admin.site.register(Event)
admin.site.register(Image)
admin.site.register(UserProfile)
admin.site.register(FaceEncoding)
