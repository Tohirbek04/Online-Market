import ast
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum, OuterRef, Exists
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView, TemplateView

from apps.forms import (OrderCreateModelForm, StreamCreateModelForm,
                        TransactionModelForm)
from apps.mixins import OperatorRequiredMixin
from apps.models import (Category, Competition, LikeModel, Order, Product,
                         SiteSetting, Stream, Transaction)
from users.models import User, Region, District


class BaseProductListView(ListView):
    queryset = Product.objects.select_related('category')

    def get_queryset(self):
        user_has_liked_subquery = LikeModel.objects.filter(user=self.request.user.id, product=OuterRef('pk'))
        return super().get_queryset().annotate(is_liked=Exists(user_has_liked_subquery))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['setting'] = SiteSetting.objects.first()
        return context


class ProductListView(BaseProductListView):
    paginate_by = 5
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
            qs = qs.filter(category__slug=slug)
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
            self._cache_stream.views_count += 1
            self._cache_stream.save()
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


class OrderListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.select_related('product')
    template_name = 'apps/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class OrderSuccessDetailView(DetailView):
    model = Order
    template_name = 'status/accepted.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        _settings = SiteSetting.objects.first()
        ctx['delivery_price'] = _settings.shopping_cost
        return ctx


class ClickLikeView(View):
    def get(self, request, pk):
        if self.request.user.is_authenticated:
            obj, created = LikeModel.objects.get_or_create(user=request.user, product_id=pk)
            if not created:
                obj.delete()
            return redirect('product_list')
        return redirect('product_list')


class LikeListView(LoginRequiredMixin, ListView):
    queryset = LikeModel.objects.select_related('product')
    template_name = 'apps/like-list.html'
    context_object_name = 'likes'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


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
        product = self.get_object()
        context = super().get_context_data(**kwargs)
        context['total_stream_count'] = product.streams.count()
        context['owner_stream_count'] = product.streams.filter(owner=self.request.user).count()
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
                    'missed_call_count',
                    'total_views_count'
                )
            )
        else:
            qs = (
                self.model.objects.select_related('streams', 'product').prefetch_related('orders').annotate(
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
                    'missed_call_count',
                    'product__title'
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
                 .annotate(order_delivered_count=Count('referral_user', filter=
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
        transaction = form.save(commit=False)
        transaction.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect('payment')


class RequestListView(ListView):
    queryset = Order.objects.all().select_related('product', 'stream', 'operator')
    template_name = 'apps/request-list.html'
    context_object_name = 'orders'


class BaseOrderListView(OperatorRequiredMixin, ListView):
    context_object_name = 'orders'
    queryset = Order.objects.all()
    paginate_by = 2

    def get_queryset(self):
        qs = super().get_queryset().filter(status=self.status)
        if product := self.request.GET.get('product', ''):
            qs = qs.filter(product__title__icontains=product)
        if region := self.request.GET.get('region'):
            qs = qs.filter(district__region_id=region)
        if district := self.request.GET.get('district'):
            qs = qs.filter(district_id=district)
        return qs.select_related('product', 'stream')

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(object_list=object_list, **kwargs)
        context_data['regions'] = Region.objects.all()
        context_data['products'] = Product.objects.all().values('id', 'title')
        return context_data


class NewOrderListView(BaseOrderListView):
    status = Order.Status.NEW
    template_name = 'apps/operator/status/operator-new-page.html'


class ReadyOrderListView(BaseOrderListView):
    status = Order.Status.READY
    template_name = 'apps/operator/status/operator-ready-page.html'


class DeliveryOrderListView(BaseOrderListView):
    status = Order.Status.DELIVERY
    template_name = 'apps/operator/status/operator-all-page.html'


class DeliveredOrderListView(BaseOrderListView):
    status = Order.Status.DELIVERED
    template_name = 'apps/operator/status/operator-all-page.html'


class CancelledOrderListView(BaseOrderListView):
    status = Order.Status.CANCELLED
    template_name = 'apps/operator/status/status-change.html'


class ArchivedOrderListView(BaseOrderListView):
    status = Order.Status.ARCHIVED
    template_name = 'apps/operator/status/status-change.html'


class AllOrderListView(OperatorRequiredMixin, ListView):
    queryset = Order.objects.select_related('product', 'stream')
    template_name = 'apps/operator/status/operator-all-page.html'
    context_object_name = 'orders'
    paginate_by = 5

    def get_queryset(self):
        qs = super().get_queryset()
        product = self.request.GET.get('product')
        if product:
            qs = qs.filter(product__title__icontains=product)
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(object_list=object_list, **kwargs)
        context_data['regions'] = Region.objects.all()
        context_data['products'] = Product.objects.only('title')
        return context_data


class OrderChangeDetailView(DetailView):
    model = Order
    template_name = 'apps/operator/accepted.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        order.operator_id = self.request.user.id
        order.save()
        context['setting'] = SiteSetting.objects.first()
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.select_related('region')
        return context


class OrderNewToReadyUpdateView(UpdateView):
    template_name = 'apps/operator/accepted.html'
    model = Order
    fields = 'quantity', 'district', 'location', 'status', 'description', 'send_order_date'
    success_url = reverse_lazy('new_orders')


class CourierPageView(View):

    def post(self, request, *args, **kwargs):
        context = {
            'couriers': User.objects.filter(type=User.Type.COURIER),
            'orders_id': request.POST.getlist('orders')
        }
        return render(request, 'apps/operator/courier.html', context)


class PrintPageView(View):
    def post(self, request, *args, **kwargs):
        courier_id = self.request.POST.get('courier_id')
        orders_list = ast.literal_eval(request.POST.get('orders'))
        for order in Order.objects.filter(pk__in=orders_list):
            order.courier_id = courier_id
            order.save()
        context = {'orders': Order.objects.filter(pk__in=orders_list).select_related('product', 'stream', 'courier',
                                                                                     'operator', 'district'),
                   'orders_id': orders_list}
        return render(request, 'apps/operator/print.html', context)


class StatusToDeliveryView(View):
    def post(self, request, *args, **kwargs):
        orders_list = ast.literal_eval(request.POST.get('orders'))
        for order in Order.objects.filter(pk__in=orders_list):
            order.status = Order.Status.DELIVERY
            order.save()
        return redirect('new_orders')


class ForbiddenStatusTemplateView(TemplateView):
    template_name = 'status/403.html'
