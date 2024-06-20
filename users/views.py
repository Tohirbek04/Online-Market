from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView, UpdateView

from users.forms import CreateForm, LoginForm, PasswordUpdateForm
from users.models import User


class RegisterView(CreateView):
    form_class = CreateForm
    template_name = "users/auth/register.html"
    success_url = reverse_lazy('login')


class UserLoginView(FormView):
    form_class = LoginForm
    success_url = reverse_lazy('settings')
    template_name = 'users/auth/login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class SettingsTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'users/auth/settings.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/auth/settings.html'
    fields = 'first_name', 'last_name', 'region', 'district', 'about'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        return self.request.user


class ImageUpdateView(UpdateView):
    model = User
    fields = 'image', 'background_image'
    template_name = 'users/auth/settings.html'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        return self.request.user


class ProfileTemplateView(TemplateView):
    template_name = 'users/auth/profile.html'
