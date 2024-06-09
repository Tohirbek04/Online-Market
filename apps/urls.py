from django.urls import path


from .views import HomeView, CategoryProductView, ProductDetailView, CreateOrderView, SearchProductView

urlpatterns = [

    path('', HomeView.as_view(), name='home'),
    path('category/<slug:slug>', CategoryProductView.as_view(), name='category'),
    path('product-detail/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('create-order/<slug:slug>', CreateOrderView.as_view(), name='create_order'),
    path('search-product/', SearchProductView.as_view(), name='search_product'),
]
