from django.contrib.auth.views import LogoutView
from django.urls import path

from users.views import (ImageUpdateView, PasswordUpdateView,
                         ProfileTemplateView, ProfileUpdateView, RegisterView,
                         SettingsTemplateView, UserLoginView)

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(next_page='/'), name='logout'),

    path('profile', ProfileTemplateView.as_view(), name='profile'),
    path('profile/settings', SettingsTemplateView.as_view(), name='settings'),
    path('profile/update', ProfileUpdateView.as_view(), name='profile_update'),

    # path('password/update', PasswordUpdateView.as_view(), name='password_update'),
    path('image/update', ImageUpdateView.as_view(), name='image_update')

]
