from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, TemplateView, ListView

from apps.models import Category, Product, Order
from users.models import User


class HomeView(View):
    def get(self, request):
        categories = Category.objects.all()
        products = Product.objects.all()
        context = {
            "categories": categories,
            "products": products

        }
        return render(request, 'web/home.html', context)


class CategoryProductView(View):

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        products = category.product_set.all()
        context = {
            'category': category,
            'products': products
        }
        return render(request, 'web/home.html', context)


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'web/product-detail.html'
    login_url = 'login'


class CreateOrderView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        if product:
            new_order = Order(user=request.user, product=product)
            new_order.save()
            return render(request, 'web/accepted.html', {"product": product})
        return render(request, 'errors/404.html')


class SearchProductView(ListView):
    template_name = 'web/home.html'
    model = Product
    context_object_name = 'products'

    def get_queryset(self):
        title = self.request.GET.get('search', '')
        if title:
            object_list = self.model.objects.filter(title__icontains=title)
            return object_list


class OrderView(ListView):
    model = Order
    context_object_name = 'orders'
    template_name = 'web/orders.html'

    def get_queryset(self):
        pass


