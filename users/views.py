from django.contrib.auth import login
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, FormView, TemplateView, UpdateView

from users.forms import CreateForm, LoginForm, PasswordUpdateForm, UserUpdateForm
from users.models import User


class RegisterView(CreateView):
    form_class = CreateForm
    template_name = "user/register.html"
    success_url = reverse_lazy('login')


class UserLoginView(FormView):
    form_class = LoginForm
    success_url = reverse_lazy('settings')
    template_name = 'user/login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class SettingsView(View):
    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)
        return render(request, 'user/settings.html', {"user": user})


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user/settings.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'user/settings.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('settings')

    def get_queryset(self):
        return super().get_queryset()
