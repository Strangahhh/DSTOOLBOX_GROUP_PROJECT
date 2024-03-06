from django.urls import path
from . import views
from django.contrib.auth.views import LoginView,PasswordResetView,PasswordResetDoneView,PasswordResetConfirmView,PasswordResetCompleteView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Authentication
    path('login/', views.login_signup_view, name='login_signup_view'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', 
        PasswordResetView.as_view(
            template_name='rubrop/password_reset.html',
            html_email_template_name='rubrop/password_reset_email.html'
        ),
        name='password-reset'
    ),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='rubrop/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='rubrop/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='rubrop/password_reset_complete.html'),name='password_reset_complete'),

    # Public Views
    path('', views.home_page_imgslide, name='home_page_img_slide'),
    path('home_page/', views.home_page, name='home_page'),
    path('create_event/', views.create_event, name='create_event'),

    # User
    path('event/<uuid:event_id>/', views.user_home, name='user_home'),
    path('event/<uuid:event_id>/matching/', views.user_event_matching, name='user_event_matching'),
    path('event/<uuid:event_id>/matching/download/', views.user_event_matching_download_images_as_zip, name='user_event_matching_download_images_as_zip'),

    # Event Management
    path('home/', views.management_event, name='management_event'),
    path('create/event/', views.management_create_event, name='management_create_event'),

    # Admin Hub
    path('adminhub/<uuid:event_id>/dashboard/', views.admin_hub_dashboard, name='admin_hub_dashboard'),
    path('adminhub/<uuid:event_id>/storage/', views.admin_hub_storage, name='admin_hub_storage'),
    path('adminhub/<uuid:event_id>/details/', views.admin_hub_details, name='admin_hub_details'),
    path('adminhub/<uuid:event_id>/team/', views.admin_hub_team, name='admin_hub_team'),

    # CRUD Staff
    path('adminhub/<uuid:event_id>/team/add/', views.add_staff, name='add_staff'),
    path('adminhub/<uuid:event_id>/team/delete/<int:user_id>/', views.delete_staff, name='delete_staff'),
    # path('adminhub/<uuid:event_id>/team/edit_role/<int:user_id>/', views.edit_staff_role, name='edit_staff_role'),

    # Upload & Download
    path('adminhub/<uuid:event_id>/storage/upload/image', views.upload_image_storage, name='upload_image_storage'),
    path('adminhub/<uuid:event_id>/storage/dowload', views.download_images_as_zip, name='download_images_as_zip'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
