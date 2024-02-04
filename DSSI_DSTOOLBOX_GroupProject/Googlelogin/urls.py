from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('sign-in', views.sign_in, name='sign_in'),
    path('enter-password/', views.enter_password, name='enter_password'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('response', views.response, name='response'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
]

