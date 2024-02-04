from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.password_validation import MinimumLengthValidator
from django.templatetags.static import static

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Remove default password validators
        self.fields['password1'].validators = [MinimumLengthValidator(8)]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Set the default profile picture URL when creating a new user
        default_image_url = static('Googlelogin/assets/image/default-profile.png')
        user.profile_picture = default_image_url

        if commit:
            user.save()
        return user
