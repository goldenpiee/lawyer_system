from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from appointments.views import client_profile

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_redirect, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset_confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('client_profile/', client_profile, name='client_profile'),
    path('confirm_email/', views.confirm_email, name='confirm_email'),
    path('client_profile/', views.client_profile, name='client_profile'),
]
