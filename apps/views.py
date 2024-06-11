from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, CreateView

from apps.models import Category, Product, Order, LikeModel


class BaseProductListView(ListView):
    queryset = Product.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductListView(BaseProductListView):
    template_name = 'apps/products/product-list.html'


class ProductByCategoryListView(BaseProductListView):
    template_name = 'apps/products/category-by-product.html'

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        qs = super().get_queryset()
        if slug:
            qs = qs.filter(category__slug=slug)
        return qs


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'apps/products/product-detail.html'


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = 'name', 'phone_number'
    template_name = 'apps/products/product-detail.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)

        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class OrderListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.select_related('product')
    template_name = 'apps/orders.html'
    context_object_name = 'orders'


class ClickLikeView(View):
    def get(self, request, pk):
        get, created = LikeModel.objects.get_or_create(user=request.user, product_id=pk)
        if not created:
            get.delete()
        return redirect('product_list')


class MarketListView(LoginRequiredMixin, ListView):
    queryset = Product.objects.all()
    template_name = 'apps/market.html'
    context_object_name = 'products'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class CategoryMarketProductView(BaseProductListView):
    template_name = 'apps/market.html'
