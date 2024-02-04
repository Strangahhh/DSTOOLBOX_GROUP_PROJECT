import os

from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.utils.decorators import method_decorator
from .models import CustomUser
from django.contrib.auth import login, logout, authenticate
from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages


def sign_in(request):
    return render(request, 'Googlelogin/sign_in.html')

def home_page(request):
    return render(request, 'Googlelogin/home_page.html')

@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']

    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)

    # Extract user data
    email = user_data['email']
    first_name = user_data.get('given_name', '')  # Get the first name
    last_name = user_data.get('family_name', '')  # Get the last name
    profile_picture = user_data.get('picture', '')  # Get the profile picture URL

    # In a real app, I'd also save any new user here to the database.
    user, created = CustomUser.objects.get_or_create(
        email=email, 
        defaults={
            'username': email,
            'first_name': first_name,
            'last_name': last_name,
            'profile_picture': profile_picture,
        })

    if not created:
        user.first_name = first_name
        user.last_name = last_name
        user.profile_picture = profile_picture
        user.save()

    # Log the user in
    login(request, user)

    request.session['user_data'] = user_data

    return redirect('response')

from django.contrib.auth import logout

def sign_out(request):
    logout(request)
    request.session.clear()
    return redirect('home_page')


def response(request):
    return render(request, 'Googlelogin/resx.html')

def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('sign_in') 
    else:
        form = RegistrationForm()

    return render(request, 'Googlelogin/sign_up.html', {'form': form})

def sign_in(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if user:
            # Store the user's email in session to use in the next step
            request.session['email_for_signin'] = email
            return redirect('enter_password')
        else:
            messages.error(request, "No account found with this email.")
    return render(request, 'Googlelogin/sign_in.html')

def enter_password(request):
    if request.method == 'POST':
        email = request.session.get('email_for_signin')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # Clear the email stored in session
            del request.session['email_for_signin']
            return redirect('response')
        else:
            messages.error(request, "Invalid password.")
            return redirect('enter_password')
    return render(request, 'Googlelogin/enter_password.html')