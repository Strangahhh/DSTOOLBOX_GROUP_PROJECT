import base64
import io
import random
import zipfile
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from .forms import AddStaffForm, EditStaffRoleForm, EventForm, FaceUploadForm, ImageUploadForm, LoginForm, SignUpForm
from django.contrib.auth.decorators import login_required
import qrcode
from io import BytesIO
from django.http import FileResponse, HttpResponse
from .models import Event, FaceEncoding, Image, UserProfile
import dlib
from django.conf import settings
import numpy as np
from django.contrib.auth import authenticate, login
from django.urls import reverse
import tempfile
import os
from PIL import Image as PILImage
import face_recognition
from django.contrib.auth import logout
from django.contrib.auth.models import User
import tempfile
import zipfile
from django.core.files.storage import default_storage
from django.contrib.auth.forms import AuthenticationForm
import urllib3
import urllib.request




### Event dashboard content ###



@login_required
def admin_hub_dashboard(request, event_id):

    event = get_object_or_404(Event, event_id=event_id)

    if not request.user == event.created_by and not request.user in event.staff_members.all():
        return render(request, 'unauthorized.html')

    images = Image.objects.filter(event=event)
    total_images = images.count()
    total_faces = FaceEncoding.objects.filter(image__event=event).count()

    total_staff = event.staff_members.count()
    
    context = {
        'event': event,
        'total_images': total_images,
        'total_faces': total_faces,
        'total_staff': total_staff
    }
    return render(request, 'rubrop/admin_dashboard.html', context)

@login_required
def admin_hub_storage(request, event_id):
        
    event = get_object_or_404(Event, event_id=event_id)

    if not request.user == event.created_by and not request.user in event.staff_members.all():
        return render(request, 'unauthorized.html')

    images = Image.objects.filter(event=event)
    total_images = images.count()
    total_faces = FaceEncoding.objects.filter(image__event=event).count()

    all_image = Image.objects.filter(event=event)

    print(len(all_image))

    total_staff = event.staff_members.count()

    context = {
        'event': event,
        'total_images': total_images,
        'total_faces': total_faces,
        'total_staff': total_staff,
        'all_image': all_image
    }

    return render(request, 'rubrop/admin_storage.html',context)

@login_required
def admin_hub_details(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)

    if not request.user == event.created_by and not request.user in event.staff_members.all():
        return render(request, 'unauthorized.html')

    images = Image.objects.filter(event=event)
    total_images = images.count()
    total_faces = FaceEncoding.objects.filter(image__event=event).count()

    # Generate QR Code
    url = request.build_absolute_uri('/event/') + str(event_id) + '/home/'
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_img_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Add QR code to context
    context = {
        'event': event,
        'total_images': total_images,
        'total_faces': total_faces,
        'qr_code': qr_img_base64,
    }
    return render(request, 'rubrop/admin_details.html', context)

@login_required
def admin_hub_team(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)

    if not request.user == event.created_by and not request.user in event.staff_members.all():
        return render(request, 'unauthorized.html')

    staff_members = event.staff_members.all() 

    context = {
        'event': event,
        'total_staff': event.staff_members.count(),
        'staff_members': staff_members,
    }
    return render(request, 'rubrop/admin_team.html', context)




###         CRUD STAFF          ###




@login_required
def add_staff(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    if request.user != event.created_by:
        return render(request, 'unauthorized.html')
    
    if request.method == 'POST':
        form = AddStaffForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                event.staff_members.add(user)
                return redirect('admin_hub_team', event_id=event_id)
            except User.DoesNotExist:
                form.add_error('username', 'Username does not exist')
    else:
        form = AddStaffForm()

    context = {
        'form': form,
        'event': event,
    }

    return render(request, 'rubrop/admin_team_add_staff.html', context)

# @login_required
# def edit_staff_role(request, event_id, user_id):
#     event = get_object_or_404(Event, event_id=event_id)
#     staff_member = get_object_or_404(User, id=user_id)

#     if request.user != event.created_by:
#         return render(request, 'unauthorized.html')

#     if request.method == 'POST':
#         form = EditStaffRoleForm(request.POST, instance=staff_member.profile)  # Corrected line
#         if form.is_valid():
#             form.save()
#             return redirect('admin_hub_team', event_id=event_id)
#     else:
#         form = EditStaffRoleForm(instance=staff_member.profile)  # Corrected line
    
#     context = {
#         'form': form,
#         'event': event,
#         'staff_member': staff_member,
#     }

#     return render(request, 'rubrop/admin_team_edit_staff.html', context)

@login_required
def delete_staff(request, event_id, user_id):
    event = get_object_or_404(Event, event_id=event_id)
    staff_member = get_object_or_404(User, id=user_id)

    if request.user != event.created_by:
        return render(request, 'unauthorized.html')

    if request.method == 'POST':
        event.staff_members.remove(staff_member)
        return redirect('admin_hub_team', event_id=event_id)

    context = {
        'event': event,
        'staff_member': staff_member,
    }

    return render(request, 'rubrop/admin_team_delete_staff.html', context)





###           Event management content           ###






def home_page_imgslide(request):
    return render(request, 'rubrop/home_page_imgslide.html')

@login_required
def management_event(request):
    user_events = Event.objects.filter(created_by=request.user)

    context = {
        'user_events': user_events
        }
    return render(request, 'rubrop/management_event.html', context)

@login_required
def management_create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            form.save_m2m()  # Since we're using a ManyToMany field for staff_members
            return redirect(reverse('admin_hub_dashboard', kwargs={'event_id': event.event_id}))
    else:
        form = EventForm()
    
    context = {
        'form': form
    }
    return render(request, 'rubrop/management_create_event.html', context)







###           User           ###




def user_home(request, event_id):
    # Assuming 'id' is the primary key field for Event
    event = get_object_or_404(Event, event_id=event_id)

    # Get all images
    all_images = list(event.images.all())

    # Create a context dictionary to hold the images for each <a> tag
    context = {
        'event': event,
        'image_sets': []
    }

    # Assuming you have a fixed number of <a> tags you want to populate
    num_of_a_tags = 12  # Update this number to match the number of <a> tags you have

    if len(all_images) >= num_of_a_tags:
        selected_images = random.sample(all_images, num_of_a_tags)
        all_images = [image for image in all_images if image not in selected_images]
        context['image_sets'].append(selected_images)
    else:
        # If the number of images is less than 12, repeat images to fill up the slots
        selected_images = random.choices(all_images, k=num_of_a_tags)
        context['image_sets'].append(selected_images)

    return render(request, 'rubrop/home_page_imgslide_user.html', context)

def user_event_matching(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)

    if request.method == 'POST':
        form = FaceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            matches = process_and_match_faces(request.FILES['image'], event)
            # Store matched images IDs in session
            request.session['matched_image_ids'] = [match.id for match in matches]
            return render(request, 'rubrop/event_matching_face_image.html', {'matches': matches, 'event': event})
    else:
        form = FaceUploadForm()
    
    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'rubrop/event_matching_face_user.html', context)

def user_event_matching_download_images_as_zip(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    matched_image_ids = request.session.get('matched_image_ids', [])
    
    # Fetch images by IDs stored in the session
    images = Image.objects.filter(id__in=matched_image_ids)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for image in images:
            # Make sure to read the image file in binary mode
            with image.image.open(mode='rb') as image_file:
                zip_file.writestr(f'{image.image.name}', image_file.read())
    
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={event.name}_images.zip'
    
    return response






###           Upload&download functions           ###




@login_required
def upload_image_storage(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.event = event
            image_instance.save()

            image_path = image_instance.image.path
            process_and_save_face_encodings(image_path, image_instance)
            return redirect(reverse('admin_hub_storage', kwargs={'event_id': event.event_id}))
    else:
        form = ImageUploadForm()

    context = {
        'form': form,
        'event': event
    }

    return render(request, 'rubrop/admin_storage_upload_image.html', context)


def upload_and_match_face(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    if request.method == 'POST':
        form = FaceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the uploaded image and find matches
            matches = process_and_match_faces(request.FILES['image'], event)
            # Display matched images
            return render(request, 'rubrop/matched_images.html', {'matches': matches})
    else:
        form = FaceUploadForm()
    return render(request, 'rubrop/upload_face.html', {'form': form, 'event': event})


def process_and_match_faces(uploaded_image, event):
    # Initialize an empty list to hold matching images
    matches = []

    # Convert the uploaded image to a format suitable for face recognition
    with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp_file:
        pil_image = PILImage.open(uploaded_image)
        pil_image.save(tmp_file, format='JPEG')
        tmp_file.seek(0)  # Go to the beginning of the file
        uploaded_image = face_recognition.load_image_file(tmp_file)

    # Extract face encodings from the uploaded image
    uploaded_encodings = face_recognition.face_encodings(uploaded_image)

    # Iterate over each face found in the uploaded image
    for uploaded_encoding in uploaded_encodings:
        # Retrieve all FaceEncoding instances associated with the event
        for face_encoding in FaceEncoding.objects.filter(image__event=event):
            # Convert the stored encoding from string back to a numpy array
            stored_encoding = np.fromstring(face_encoding.encoded[1:-1], sep=',')
            
            # Use face_recognition to compare the uploaded face with the stored face
            distance = face_recognition.face_distance([stored_encoding], uploaded_encoding)[0]
            if distance < 0.4:  # assuming 0.6 as a threshold for face match
                if face_encoding.image not in matches:
                    matches.append(face_encoding.image)

    return matches


@login_required
def download_images_as_zip(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    images = Image.objects.filter(event=event)

    # Create a BytesIO buffer to store the zip file
    zip_buffer = io.BytesIO()

    # Create a ZipFile object
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for image in images:
            # Add each image to the zip file
            zip_file.writestr(f'{image.image.name}', image.image.read())

    # Seek to the beginning of the buffer
    zip_buffer.seek(0)

    # Create a Django HttpResponse object to return the zip file
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={event.name}_images.zip'
    
    return response


###           content           ###






@login_required
def home_page(request):
    # Fetch events created by the logged-in user
    user_events = Event.objects.filter(created_by=request.user)
    
    # Pass the events to the template
    context = {'user_events': user_events}
    return render(request, 'rubrop/home_page.html', context)

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            form.save_m2m()  # Since we're using a ManyToMany field for staff_members
            return redirect(reverse('event_dashboard', kwargs={'event_id': event.event_id}))
    else:
        form = EventForm()
    return render(request, 'rubrop/create_event.html', {'form': form})

@login_required
def event_dashboard(request, event_id):
    # Retrieve the event by ID
    event = get_object_or_404(Event, event_id=event_id)

    # Ensure the user requesting the dashboard is authorized to view it
    if not request.user == event.created_by and not request.user in event.staff_members.all():
        return render(request, 'unauthorized.html')  # Or use Django's permission denied view

    # Gather data for the dashboard
    images = Image.objects.filter(event=event)
    total_images = images.count()
    # Example of additional data you might want to calculate:
    # Total faces detected in all images of this event
    total_faces = FaceEncoding.objects.filter(image__event=event).count()

    # Pass the data to the template
    context = {
        'event': event,
        'total_images': total_images,
        'total_faces': total_faces,
        # Include any other context variables here
    }
    return render(request, 'rubrop/event_dashboard.html', context)

# def generate_qr_code(request, event_id):
#     # Construct the URL for the event's page
#     url = request.build_absolute_uri('/event_page/') + str(event_id) + str('/upload_and_match_face/')
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(url)
#     qr.make(fit=True)

#     img = qr.make_image(fill_color="black", back_color="white")
#     response = HttpResponse(content_type="image/png")
#     img.save(response, "PNG")
#     return response

@login_required
def upload_image(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.event = event
            image_instance.save()

            image_path = image_instance.image.path
            process_and_save_face_encodings(image_path, image_instance)
            return redirect(reverse('event_dashboard', kwargs={'event_id': event.event_id}))
    else:
        form = ImageUploadForm()
    return render(request, 'rubrop/upload_image.html', {'form': form, 'event': event})

def process_and_save_face_encodings(image_path, image_instance):
    # Load the image using face_recognition
    loaded_image = face_recognition.load_image_file(image_path)

    # Find all face encodings in the image
    face_encodings = face_recognition.face_encodings(loaded_image)
    
    # Iterate over each face encoding found
    for encoding in face_encodings:
        # Convert the encoding from a numpy array to a list for storage
        encoding_list = encoding.tolist()
        
        # Create and save a FaceEncoding instance for each face found
        FaceEncoding.objects.create(
            image=image_instance,
            encoded=encoding_list,  # Assuming the `encoded` field can store a list
            # If your `FaceEncoding` model links to an event, add that relationship too
            event=image_instance.event
        )

def upload_and_match_face(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    if request.method == 'POST':
        form = FaceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the uploaded image and find matches
            matches = process_and_match_faces(request.FILES['image'], event)
            # Display matched images
            return render(request, 'rubrop/matched_images.html', {'matches': matches})
    else:
        form = FaceUploadForm()
    return render(request, 'rubrop/upload_face.html', {'form': form, 'event': event})

def process_and_match_faces(uploaded_image, event):
    # Initialize an empty list to hold matching images
    matches = []

    # Convert the uploaded image to a format suitable for face recognition
    with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp_file:
        pil_image = PILImage.open(uploaded_image)
        pil_image.save(tmp_file, format='JPEG')
        tmp_file.seek(0)  # Go to the beginning of the file
        uploaded_image = face_recognition.load_image_file(tmp_file)

    # Extract face encodings from the uploaded image
    uploaded_encodings = face_recognition.face_encodings(uploaded_image)

    # Iterate over each face found in the uploaded image
    for uploaded_encoding in uploaded_encodings:
        # Retrieve all FaceEncoding instances associated with the event
        for face_encoding in FaceEncoding.objects.filter(image__event=event):
            # Convert the stored encoding from string back to a numpy array
            stored_encoding = np.fromstring(face_encoding.encoded[1:-1], sep=',')
            
            # Use face_recognition to compare the uploaded face with the stored face
            distance = face_recognition.face_distance([stored_encoding], uploaded_encoding)[0]
            if distance < 0.4:  # assuming 0.6 as a threshold for face match
                if face_encoding.image not in matches:
                    matches.append(face_encoding.image)

    return matches

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home_page') 
    else:
        form = SignUpForm()
    return render(request, 'rubrop/signup.html', {'form': form})

# def my_login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('success_page')
#             else:
#                 return HttpResponse("Invalid login details supplied.")
#     else:
#         form = LoginForm()
#     return render(request, 'rubrop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login_signup_view')

def login_signup_view(request):
    # Initialize the forms here to ensure they are always defined
    signup_form = SignUpForm()
    login_form = AuthenticationForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'signup':
            signup_form = SignUpForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Make sure to use correct backend
                return redirect('management_event')  # Replace 'home' with the name of your homepage URL
            # Note: No else needed here as signup_form is already redefined if not valid
        elif action == 'login':
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('management_event')  
    context = {
        'signup_form': signup_form,
        'login_form': login_form
    }
    return render(request, 'rubrop/login.html', context)