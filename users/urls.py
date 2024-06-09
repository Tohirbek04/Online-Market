from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import UserLoginView, SettingsView, ChangePasswordView, UserUpdateView

from users.views import RegisterView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('update-user/', UserUpdateView.as_view(), name='update_user'),
    path('update/password/', ChangePasswordView.as_view(), name='update_password'),
]

