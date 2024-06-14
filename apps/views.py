from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, FormView, CreateView

from apps.forms import OrderCreateModelForm, StreamCreateModelForm
from apps.models import Category, Product, Order, LikeModel, Stream


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


class StreamCreateView(LoginRequiredMixin, CreateView):
    model = Stream
    template_name = 'apps/market.html'
    form_class = StreamCreateModelForm
    success_url = reverse_lazy('product_list')

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


class StreamListView(LoginRequiredMixin, ListView):
    template_name = 'apps/stream-list.html'
    model = Stream

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['streams'] = self.model.objects.filter(owner=self.request.user)
        return context


class StreamDetailView(DetailView):
    template_name = 'apps/products/product-detail.html'
    model = Stream

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        context = super().get_context_data(**kwargs)
        stream = self.object
        product = Product.objects.get(pk=stream.product.pk)
        context['price'] = product.price - stream.discount
        context['product'] = product
        return context
