from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', LoginView.as_view(template_name='rubrop/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Public Views
    path('', views.home_page_imgslide, name='home_page_img_slide'),
    path('home_page/', views.home_page, name='home_page'),
    path('create_event/', views.create_event, name='create_event'),

    # Event Management
    path('home/', views.management_event, name='management_event'),
    path('create/event/', views.management_create_event, name='management_create_event'),

    # Event Dashboard and Actions
    path('event/<uuid:event_id>/', views.event_dashboard, name='event_dashboard'),
    path('event/<uuid:event_id>/generate_qr_code/', views.generate_qr_code, name='generate_qr_code'),
    path('event/<uuid:event_id>/upload_image/', views.upload_image, name='upload_image'),
    path('event/<uuid:event_id>/upload_and_match_face/', views.upload_and_match_face, name='upload_and_match_face'),

    # Admin Hub
    path('adminhub/<uuid:event_id>/dashboard/', views.admin_hub_dashboard, name='admin_hub_dashboard'),
    path('adminhub/<uuid:event_id>/database/', views.admin_hub_storage, name='admin_hub_storage'),
    path('adminhub/<uuid:event_id>/details/', views.admin_hub_details, name='admin_hub_details'),
    path('adminhub/<uuid:event_id>/team/', views.admin_hub_team, name='admin_hub_team'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)