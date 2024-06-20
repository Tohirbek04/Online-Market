from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView

from apps.forms import OrderCreateModelForm, StreamCreateModelForm
from apps.models import Category, Competition, LikeModel, Order, Product, Stream
from users.models import User


class BaseProductListView(ListView):
    queryset = Product.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductListView(BaseProductListView):
    paginate_by = 3
    template_name = 'apps/products/product-list.html'


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['price'] = self.object.price
        return context


class OrderCreateView(FormView):
    template_name = 'apps/products/product-detail.html'
    form_class = OrderCreateModelForm

    def form_valid(self, form):
        order = form.save(commit=False)
        if self.request.user.is_authenticated:
            order.user = self.request.user
        order.save()
        return redirect('status_success', order.product_id)


class OrderListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.all()
    template_name = 'apps/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class OrderSuccessDetailView(DetailView):
    model = Product
    template_name = 'status/accepted.html'
    context_object_name = 'product'


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


class StreamDetailView(LoginRequiredMixin, DetailView):
    template_name = 'apps/products/product-detail.html'
    model = Stream
    context_object_name = 'stream'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stream = self.object
        stream.views_count += 1
        stream.save()
        product = Product.objects.get(pk=stream.product.pk)
        context['price'] = product.price - stream.discount
        context['product'] = product
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
                    'product__title',
                    'views_count',
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
                    new_count=Count('orders', filter=Q(orders__status=Order.Status.NEW)),
                    ready_count=Count('orders', filter=Q(orders__status=Order.Status.READY)),
                    delivery_count=Count('orders', filter=Q(orders__status=Order.Status.DELIVERY)),
                    delivered_count=Count('orders', filter=Q(orders__status=Order.Status.DELIVERED)),
                    cancelled_count=Count('orders', Q(orders__status=Order.Status.CANCELLED)),
                    archived_count=Count('orders', filter=Q(orders__status=Order.Status.ARCHIVED)),
                    missed_call_count=Count('orders', filter=Q(orders__status=Order.Status.MISSED_CALL)),

                ).values(
                    'product__title',
                    'views_count',
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
            summa_views_count=Sum('views_count'),
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
        if competition := get_object_or_404(Competition, is_active=True):
            start_date = competition.start_date
            end_date = competition.end_date
            qs = ((self.model.objects.prefetch_related('referral_user').annotate
                (order_delivered_count=Count('referral_user', filter=Q
                (referral_user__created_at__range=(start_date, end_date)) & Q
                (referral_user__status=Order.Status.DELIVERED)))).values
                (
                'first_name',
                'order_delivered_count'
                )).order_by('-order_delivered_count')
            return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx['competition'] = get_object_or_404(Competition, is_active=True)
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





