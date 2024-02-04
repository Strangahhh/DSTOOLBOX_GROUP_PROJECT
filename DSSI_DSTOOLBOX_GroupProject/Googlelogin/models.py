from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import uuid

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)  # Ensure email uniqueness
    profile_picture = models.URLField(null=True, blank=False)  # Allow for no profile picture
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email if self.email else uuid.uuid4().hex[:30]
        else:
            # Ensure username uniqueness by appending a UUID if necessary (basic example)
            while CustomUser.objects.filter(username=self.username).exists():
                self.username = f'{uuid.uuid4().hex[:30]}'
        super().save(*args, **kwargs)
