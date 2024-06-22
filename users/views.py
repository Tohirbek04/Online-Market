from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.cache import cache
from django.db.models import Case, F, IntegerField, Q, Sum, When
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, TemplateView, UpdateView

from apps.models import Order, SiteSetting, Transaction
from users.forms import CreateForm, LoginForm, UpdateModelForm, PasswordUpdateForm
from users.models import District, Region, User


class RegisterView(CreateView):
    form_class = CreateForm
    template_name = "users/auth/register.html"
    success_url = reverse_lazy('login')


class UserLoginView(FormView):
    form_class = LoginForm
    # redirect_authenticated_user = True
    template_name = 'users/auth/login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_success_url(self):
        user: User = self.request.user
        if user.type == user.Type.CLIENT:
            return reverse_lazy('profile_update')
        if user.type == user.Type.OPERATOR:
            return reverse_lazy('new_orders')


class LoginFromTelegramBotTemplateView(TemplateView):
    template_name = 'users/auth/login-bot.html'


class LoginCheckView(View):
    def post(self, request, *args, **kwargs):
        code = request.POST.get('code', '')

        if len(code) != 6:
            return JsonResponse({'msg': 'error code'}, status=400)
        phone = cache.get(code)
        if phone is None:
            return JsonResponse({'msg': 'expired code'}, status=400)
        try:
            user = User.objects.get(phone=phone)
            login(request, user)
            return redirect('profile')
        except User.DoesNotExist:
            return JsonResponse({'msg': 'user not found'}, status=400)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/auth/settings.html'
    form_class = UpdateModelForm
    success_url = reverse_lazy('profile_update')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        if region_id := self.request.user.region:
            context['districts'] = District.objects.filter(region_id=region_id)
        return context


class ImageUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = 'image', 'background_image'
    template_name = 'users/auth/settings.html'
    success_url = reverse_lazy('profile_update')

    def get_object(self, queryset=None):
        return self.request.user


class PasswordUpdateView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordUpdateForm
    template_name = 'users/auth/settings.html'
    success_url = reverse_lazy('profile_update')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs


class ProfileTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'users/auth/profile.html'


class PaymentDetailView(LoginRequiredMixin, TemplateView):
    model = Transaction
    template_name = 'users/payment.html'

    def get_queryset(self):
        qs = (Order.objects.annotate(
            referral_user_possibly_extra_balance=Sum(Case(When(
                Q(status=Order.Status.DELIVERY) &
                Q(referral_user=self.request.user), then=F('product__extra_balance') * F('quantity')),
                default=0, output_field=IntegerField())
            ),
            referral_user_possibly_discount=Sum(Case(When(
                Q(status=Order.Status.DELIVERY) &
                Q(stream__owner=self.request.user), then=F('stream__discount') * F('quantity')),
                default=0, output_field=IntegerField())
            ),

            operator_order_delivered=Sum(Case(When(
                Q(operator=self.request.user) &
                Q(status=Order.Status.DELIVERED), then='quantity'),
                default=0, output_field=IntegerField())
            ),

            operator_order_delivery=Sum(Case(When(
                Q(operator=self.request.user) &
                Q(status=Order.Status.DELIVERY), then='quantity'),
                default=0, output_field=IntegerField())
            ),

            courier_order_delivered=Sum(Case(When(
                Q(courier=self.request.user) &
                Q(status=Order.Status.DELIVERED), then=1),
                default=0, output_field=IntegerField())
            ),

            courier_order_delivery=Sum(Case(When(
                Q(courier=self.request.user) &
                Q(status=Order.Status.DELIVERY), then=1),
                default=0, output_field=IntegerField())
            )
        )
        ).values(
            'referral_user_possibly_extra_balance',
            'referral_user_possibly_discount',
            'operator_order_delivered',
            'operator_order_delivery',
            'courier_order_delivered',
            'courier_order_delivery')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(**self.get_queryset().aggregate(
            referral_user_total_possibly_extra_balance=Sum('referral_user_possibly_extra_balance'),
            referral_user_total_possibly_discount=Sum('referral_user_possibly_discount'),
            operator_order_delivered_count=Sum('operator_order_delivered'),
            operator_order_delivery_count=Sum('operator_order_delivery'),
            courier_order_delivered_count=Sum('courier_order_delivered'),
            courier_order_delivery_count=Sum('courier_order_delivery')
        ))
        site_settings = SiteSetting.objects.first()
        user_possibly_balance = (
                context['referral_user_total_possibly_extra_balance']
                - context['referral_user_total_possibly_discount']
                + site_settings.operator_sum * context['operator_order_delivery_count']
                + site_settings.shopping_cost * context['courier_order_delivery_count'])
        context['user_possibly_balance'] = user_possibly_balance
        return context


def get_district_by_region(request, region_id):
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)
