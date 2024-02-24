from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from .forms import EventForm, FaceUploadForm, ImageUploadForm, SignUpForm
from django.contrib.auth.decorators import login_required
import qrcode
from io import BytesIO
from django.http import HttpResponse
from .models import Event, FaceEncoding, Image
import dlib
from django.conf import settings
import numpy as np
from django.contrib.auth import login
from django.urls import reverse
import tempfile
import os
from PIL import Image as PILImage
import face_recognition

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

def generate_qr_code(request, event_id):
    # Construct the URL for the event's page
    url = request.build_absolute_uri('/event_page/') + str(event_id) + str('/upload_and_match_face/')
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

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
            login(request, user)  # Log the user in
            return redirect('home_page')  # Redirect to a home or dashboard page
    else:
        form = SignUpForm()
    return render(request, 'rubrop/signup.html', {'form': form})
