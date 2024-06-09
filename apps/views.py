from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, TemplateView

from apps.models import Category, Product, Order


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
        products = Product.objects.filter(category=category)
        context = {
            'category': category,
            'products': products
        }
        return render(request, 'web/home.html', context)


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'web/product-detail.html'
    login_url = 'login'


class CreateOrderView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        if product:
            new_order = Order(user=request.user, product=product)
            new_order.save()
            return redirect('home')
        return render(request, 'errors/404.html')




