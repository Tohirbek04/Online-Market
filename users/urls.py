from django.contrib.auth.views import LogoutView
from django.urls import path

from users.views import (ImageUpdateView, LoginFromTelegramBotTemplateView,
                         PaymentDetailView, ProfileTemplateView,
                         ProfileUpdateView, RegisterView,
                         UserLoginView, get_district_by_region, LoginCheckView)

urlpatterns = [
    path('sign_up', RegisterView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(next_page='/login'), name='logout'),
    path('bot/login', LoginFromTelegramBotTemplateView.as_view(), name='bot_login'),
    path('login-check', LoginCheckView.as_view(), name='login_check'),

    path('profile', ProfileTemplateView.as_view(), name='profile'),

    path('update/profile', ProfileUpdateView.as_view(), name='profile_update'),
    path('update/image', ImageUpdateView.as_view(), name='image_update'),
    path('update/password', ImageUpdateView.as_view(), name='password_update'),


    path('payment', PaymentDetailView.as_view(), name='payment'),

    path('ajax/get-district/<int:region_id>', get_district_by_region, name='get_districts')


]
