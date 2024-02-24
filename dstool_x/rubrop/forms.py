from django import forms
from .models import Event, Image
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'location', 'date_time', 'staff_members']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'staff_members': forms.SelectMultiple()
        }

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

class FaceUploadForm(forms.Form):
    image = forms.ImageField()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)