from django import forms
from .models import Event, Image, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'location', 'description', 'date_time']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

class FaceUploadForm(forms.Form):
    image = forms.ImageField()

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)

class AddStaffForm(forms.Form):
    username = forms.CharField()

class EditStaffRoleForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = UserProfile.ROLE_CHOICES

class FaceUploadForm(forms.Form):
    image = forms.ImageField()