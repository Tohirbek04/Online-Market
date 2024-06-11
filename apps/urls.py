from django.urls import path


from apps.views import ProductDetailView, OrderListView, ProductListView, ProductByCategoryListView, OrderCreateView, \
    ClickLikeView, MarketListView, CategoryMarketProductView

urlpatterns = [

    path('', ProductListView.as_view(), name='product_list'),
    path('category/<slug:slug>', ProductByCategoryListView.as_view(), name='product_by_category'),
    path('product/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('orders', OrderListView.as_view(), name='order_list'),
    path('create-order', OrderCreateView.as_view(), name='create_order'),
    # path('search-product/', SearchProductView.as_view(), name='search_product'),
    path('click-like/<int:pk>', ClickLikeView.as_view(), name='click_like'),
    path('market/', MarketListView.as_view(), name='market'),
    path('category-market/<slug:slug>', CategoryMarketProductView.as_view(), name='category_market'),
]
