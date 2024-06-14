from django.urls import path

from apps.views import ProductDetailView, OrderListView, ProductListView, ProductByCategoryListView, OrderCreateView, \
    ClickLikeView, MarketListView, CategoryMarketProductView, LikeListView, OrderSuccessDetailView, StreamCreateView, \
    StreamListView, StreamDetailView

urlpatterns = [

    path('', ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),

    path('category/<slug:slug>', ProductByCategoryListView.as_view(), name='product_by_category'),
    path('category-market/<slug:slug>', CategoryMarketProductView.as_view(), name='category_by_product_market'),

    path('orders', OrderListView.as_view(), name='order_list'),
    path('create/order', OrderCreateView.as_view(), name='create_order'),

    path('click-like/<int:pk>', ClickLikeView.as_view(), name='click_like'),
    path('product/like', LikeListView.as_view(), name='like_list'),

    path('market', MarketListView.as_view(), name='market'),

    path('status/success/<int:pk>', OrderSuccessDetailView.as_view(), name='status_success'),

    path('stream', StreamCreateView.as_view(), name='stream'),
    path('stream/list', StreamListView.as_view(), name='stream_list'),
    path('stream/<int:pk>', StreamDetailView.as_view(), name='stream_detail'),
]
