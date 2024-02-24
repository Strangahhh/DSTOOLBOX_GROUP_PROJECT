from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Simplify URL paths
    path('home_page/', views.home_page, name='home_page'),
    path('create_event/', views.create_event, name='create_event'),
    path('event/<uuid:event_id>/dashboard/', views.event_dashboard, name='event_dashboard'),
    path('event/<uuid:event_id>/generate_qr_code/', views.generate_qr_code, name='generate_qr_code'),
    path('event/<uuid:event_id>/upload_image/', views.upload_image, name='upload_image'),
    path('event/<uuid:event_id>/upload_and_match_face/', views.upload_and_match_face, name='upload_and_match_face'),
    path('signup/', views.signup, name='signup'),
    path('', LoginView.as_view(template_name='rubrop/login.html'), name='login'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)