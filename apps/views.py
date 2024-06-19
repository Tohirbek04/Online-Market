from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView

from apps.forms import OrderCreateModelForm, StreamCreateModelForm
from apps.models import Category, LikeModel, Order, Product, Stream


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
        if self.request.user.id:
            order.user = self.request.user
        order.save()
        return redirect('status_success', order.product_id)


class OrderListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.all()
    template_name = 'apps/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        qs = self.queryset.filter(user=self.request.user)
        return qs


class OrderSuccessDetailView(DetailView):
    model = Product
    template_name = 'status/accepted.html'
    context_object_name = 'product'


class ClickLikeView(View):
    def get(self, request, pk):
        get, created = LikeModel.objects.get_or_create(user=request.user, product_id=pk)
        if not created:
            get.delete()
        return redirect('product_list')


class LikeListView(ListView):
    queryset = LikeModel.objects.all()
    template_name = 'apps/like-list.html'
    context_object_name = 'likes'

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset


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


class StreamDetailView(DetailView):
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


class ProductStatisticsDetailView(DetailView):
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


class StatisticsView(ListView):
    template_name = 'apps/statistics.html'
    context_object_name = 'streams'

    def get_queryset(self):
        queryset = (Stream.objects.select_related('product').prefetch_related('order').annotate(
            new_count=Count('order', filter=Q(order__status=Order.Status.NEW)),
            ready_count=Count('order', filter=Q(order__status=Order.Status.READY)),
            delivery_count=Count('order', filter=Q(order__status=Order.Status.DELIVERY)),
            delivered_count=Count('order', filter=Q(order__status=Order.Status.DELIVERED)),
            cancelled_count=Count('order', Q(order__status=Order.Status.CANCELLED)),
            archived_count=Count('order', filter=Q(order__status=Order.Status.ARCHIVED)),
            missed_call_count=Count('order', filter=Q(order__status=Order.Status.MISSED_CALL))
        )).values(
            'product__title',
            'views_count',
            'name',
            'owner__id',
            'new_count',
            'ready_count',
            'delivery_count',
            'delivered_count',
            'cancelled_count',
            'archived_count',
            'missed_call_count')
        return queryset

