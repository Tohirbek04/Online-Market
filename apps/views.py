from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum, OuterRef, Case, BooleanField, When, Subquery, Exists
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView

from apps.forms import (OrderCreateModelForm, StreamCreateModelForm,
                        TransactionModelForm)
from apps.mixins import OperatorRequiredMixin
from apps.models import (Category, Competition, LikeModel, Order, Product,
                         SiteSetting, Stream, Transaction)
from users.models import User


class BaseProductListView(ListView):
    queryset = Product.objects.select_related('category')

    def get_queryset(self):
        user_has_liked_subquery = LikeModel.objects.filter(user=self.request.user, product=OuterRef('pk'))
        return super().get_queryset().annotate(is_liked=Exists(user_has_liked_subquery))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['setting'] = SiteSetting.objects.first()
        return context


class ProductListView(BaseProductListView):
    paginate_by = 10
    template_name = 'apps/products/product-list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if search := self.request.GET.get('search'):
            qs = qs.filter(title__icontains=search)
            return qs
        return qs


class ProductByCategoryListView(BaseProductListView):
    template_name = 'apps/products/category-by-product.html'
    paginate_by = 3

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        qs = super().get_queryset()
        if slug:
            qs = qs.filter(category__slug=slug).select_related('category')
        return qs


class ProductDetailView(DetailView):
    model = Product
    template_name = 'apps/products/product-detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        self._cache_stream = None
        if pk is not None:
            self._cache_stream = get_object_or_404(Stream.objects.all(), pk=pk)
            return self._cache_stream.product
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        price = self.object.price
        if self._cache_stream:
            price -= self._cache_stream.discount

        ctx['stream_id'] = self.kwargs.get(self.pk_url_kwarg, '')
        ctx['price'] = price
        return ctx


class OrderCreateView(FormView):
    template_name = 'apps/products/product-detail.html'
    form_class = OrderCreateModelForm

    def form_valid(self, form):
        order = form.save(commit=False)
        if stream_id := self.request.POST.get('stream'):
            order.referral_user = get_object_or_404(Stream, pk=stream_id).owner
        if self.request.user.is_authenticated:
            order.user = self.request.user
        order.save()
        return redirect('status_success', order.id)

    def form_invalid(self, form):
        return super().form_invalid(form)


class OrderListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.all()
    template_name = 'apps/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).select_related('product')


class OrderSuccessDetailView(DetailView):
    model = Order
    template_name = 'status/accepted.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        _settings = SiteSetting.objects.first()
        ctx['delivery_price'] = _settings.shopping_cost or 0
        return ctx


class ClickLikeView(View):
    def get(self, request, pk):
        obj, created = LikeModel.objects.get_or_create(user=request.user, product_id=pk)
        if not created:
            obj.delete()
        return redirect('product_list')


class LikeListView(ListView):
    queryset = LikeModel.objects.all()
    template_name = 'apps/like-list.html'
    context_object_name = 'likes'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).select_related('product')


class MarketListView(LoginRequiredMixin, ListView):
    queryset = Product.objects.all()
    template_name = 'apps/market.html'
    context_object_name = 'products'
    paginate_by = 3

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self):
        if search := self.request.GET.get('search'):
            qs = self.queryset.filter(title__icontains=search)
            return qs
        return super().get_queryset()


class CategoryMarketProductView(MarketListView):

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        qs = super().get_queryset()
        if slug:
            qs = qs.filter(category__slug=slug)
        return qs


class StreamCreateListView(LoginRequiredMixin, CreateView, ListView):
    model = Stream
    form_class = StreamCreateModelForm
    success_url = reverse_lazy('product_list')

    def get_template_names(self):
        if self.request.method == "POST":
            return 'apps/market.html'
        return 'apps/stream-list.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        stream = form.save(commit=False)
        stream.owner = self.request.user
        stream.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect('market')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['streams'] = self.model.objects.filter(owner=self.request.user)
        return context


class ProductStatisticsDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'apps/products/product-stats.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        slug = self.kwargs.get(self.slug_url_kwarg)
        product = self.model.objects.get(slug=slug)
        context = super().get_context_data(**kwargs)
        context['total_stream_count'] = Stream.objects.filter(product_id=product.id).count()
        context['owner_stream_count'] = Stream.objects.filter(product_id=product.id, owner=self.request.user).count()
        return context


class StatisticsView(LoginRequiredMixin, ListView):
    model = Stream
    template_name = 'apps/statistics.html'
    context_object_name = 'streams'

    def get_queryset(self):
        now = timezone.now()

        data = {
            "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
            "last_day": (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
            "weekly": (now - timedelta(weeks=1)).replace(hour=0, minute=0, second=0, microsecond=0),
            "monthly": (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0),
            "all": None
        }
        period = self.request.GET.get("period", "all")
        start_date = data[period]
        if start_date:
            qs = (
                self.model.objects.select_related('streams').prefetch_related('orders').annotate(
                    total_views_count=Count('views_count', filter=Q(orders__created_at__gte=start_date)),
                    new_count=Count('orders', filter=Q(orders__status=Order.Status.NEW) & Q(
                        orders__created_at__gte=start_date)),
                    ready_count=Count('orders', filter=Q(orders__status=Order.Status.READY) & Q(
                        orders__created_at__gte=start_date)),
                    delivery_count=Count('orders', filter=Q(orders__status=Order.Status.DELIVERY) & Q(
                        orders__created_at__gte=start_date)),
                    delivered_count=Count('orders', filter=Q(orders__status=Order.Status.DELIVERED) & Q(
                        orders__created_at__gte=start_date)),
                    cancelled_count=Count('orders', Q(orders__status=Order.Status.CANCELLED) & Q(
                        orders__created_at__gte=start_date)),
                    archived_count=Count('orders', filter=Q(orders__status=Order.Status.ARCHIVED) & Q(
                        orders__created_at__gte=start_date)),
                    missed_call_count=Count('orders', filter=Q(orders__status=Order.Status.MISSED_CALL) & Q(
                        orders__created_at__gte=start_date)),

                ).values(
                    'total_views_count',
                    'product__title',
                    'name',
                    'new_count',
                    'ready_count',
                    'delivery_count',
                    'delivered_count',
                    'cancelled_count',
                    'archived_count',
                    'missed_call_count'
                )
            )
        else:
            qs = (
                self.model.objects.select_related('streams').prefetch_related('orders').annotate(
                    total_views_count=Count('orders'),
                    new_count=Count('orders', filter=Q(orders__status=Order.Status.NEW)),
                    ready_count=Count('orders', filter=Q(orders__status=Order.Status.READY)),
                    delivery_count=Count('orders', filter=Q(orders__status=Order.Status.DELIVERY)),
                    delivered_count=Count('orders', filter=Q(orders__status=Order.Status.DELIVERED)),
                    cancelled_count=Count('orders', Q(orders__status=Order.Status.CANCELLED)),
                    archived_count=Count('orders', filter=Q(orders__status=Order.Status.ARCHIVED)),
                    missed_call_count=Count('orders', filter=Q(orders__status=Order.Status.MISSED_CALL)),

                ).values(
                    'total_views_count',
                    'product__title',
                    'name',
                    'new_count',
                    'ready_count',
                    'delivery_count',
                    'delivered_count',
                    'cancelled_count',
                    'archived_count',
                    'missed_call_count'
                )
            )
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx.update(**self.get_queryset().aggregate(
            summa_views_count=Sum('total_views_count'),
            summa_new_count=Sum('new_count'),
            summa_ready_count=Sum('ready_count'),
            summa_delivery_count=Sum('delivery_count'),
            summa_delivered_count=Sum('delivered_count'),
            summa_cancelled_count=Sum('cancelled_count'),
            summa_archived_count=Sum('archived_count'),
            summa_missed_call_count=Sum('missed_call_count')
        ))
        return ctx


class CompetitionListView(LoginRequiredMixin, ListView):
    template_name = 'apps/competition.html'
    model = User
    context_object_name = 'users'

    def get_queryset(self):
        self.competition = get_object_or_404(Competition, is_active=True)
        if self.competition:
            start_date = self.competition.start_date
            end_date = self.competition.end_date
            qs = (
                (self.model.objects.prefetch_related('referral_user')
                 .annotate(order_delivered_count=
                           Count('referral_user', filter=
                           Q(referral_user__created_at__range=(start_date, end_date)) &
                           Q(referral_user__status=Order.Status.DELIVERED)))
                 ).values('first_name', 'order_delivered_count')
            ).order_by('-order_delivered_count')
            return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx['competition'] = self.competition
        return ctx


class TopProductListView(ListView):
    template_name = 'apps/market.html'
    context_object_name = 'products'
    queryset = Product.objects.prefetch_related('orders').annotate(
        delivered_count=Count('orders', orders__status=Order.Status.DELIVERED)
    ).values(
        'title',
        'slug',
        'image',
        'count',
        'extra_balance',
        'price',
        'delivered_count'
    ).order_by('-delivered_count')[:5]

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx['categories'] = Category.objects.all()
        return ctx


class TransactionDetailView(LoginRequiredMixin, CreateView):
    template_name = 'users/payment.html'
    model = Transaction
    form_class = TransactionModelForm
    success_url = reverse_lazy('payment')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        tr = form.save(commit=False)
        tr.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect('payment')


class RequestListView(ListView):
    queryset = Order.objects.all().select_related('product', 'stream', 'operator')
    template_name = 'apps/request-list.html'
    context_object_name = 'orders'


class BaseOrderListView(OperatorRequiredMixin, ListView):
    template_name = 'users/employees/operator.html'
    context_object_name = 'orders'
    queryset = Order.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(status=self.status).select_related('orders').values(
            'pk',
            'product__title',
            'stream',
            'created_at',
            'phone_number',
            'name',
            'quantity',
            'stream__discount',
            'product__price'
        )


class NewOrderListView(BaseOrderListView):
    status = Order.Status.NEW


class ReadyOrderListView(BaseOrderListView):
    status = Order.Status.READY


class DeliveryOrderListView(BaseOrderListView):
    status = Order.Status.DELIVERY


class DeliveredOrderListView(BaseOrderListView):
    status = Order.Status.DELIVERED


class CancelledOrderListView(BaseOrderListView):
    status = Order.Status.CANCELLED


class ArchivedOrderListView(BaseOrderListView):
    status = Order.Status.ARCHIVED


class MissedCallOrderListView(BaseOrderListView):
    status = Order.Status.MISSED_CALL
