from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView, UpdateView, DetailView

from apps.models import Order
from users.forms import CreateForm, LoginForm
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


class ImageUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = 'image', 'background_image'
    template_name = 'users/auth/settings.html'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        return self.request.user


class ProfileTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'users/auth/profile.html'


class PaymentDetailView(LoginRequiredMixin, DetailView):
    template_name = 'users/payment.html'
    model = Order

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        real_balance = self.calculate_real_balance()
        user = get_object_or_404(User, pk=self.request.user.pk)
        if user.balance != real_balance:
            user.balance = real_balance
            user.save()
        context['real_balance'] = real_balance
        context['possibly_balance'] = self.calculate_possibly_balance()
        return context

    def calculate_real_balance(self):
        total_real_extra_balance = sum(self.model.objects.filter
            (
                Q(referral_user=self.request.user) &
                Q(status=self.model.Status.DELIVERED)).
                values_list('product__extra_balance', flat=True)
            )
        total_real_discount = sum(self.model.objects.filter
            (
                Q(stream__owner=self.request.user) &
                Q(status=self.model.Status.DELIVERED)).
                values_list('stream__discount', flat=True)
            )

        return total_real_extra_balance - total_real_discount

    def calculate_possibly_balance(self):
        total_possibly_extra_balance = sum(self.model.objects.filter
            (
                Q(referral_user=self.request.user) &
                Q(status=self.model.Status.DELIVERY)).
                values_list('product__extra_balance', flat=True)
            )
        total_possibly_discount = sum(self.model.objects.filter
            (
                Q(stream__owner=self.request.user) &
                Q(status=self.model.Status.DELIVERY)).
                values_list('stream__discount', flat=True)
            )

        return total_possibly_extra_balance - total_possibly_discount
