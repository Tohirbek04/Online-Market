from django.urls import path

from apps.views import (CategoryMarketProductView, ClickLikeView,
                        CompetitionListView, LikeListView, MarketListView,
                        OrderCreateView, OrderListView, OrderSuccessDetailView,
                        ProductByCategoryListView, ProductDetailView,
                        ProductListView, ProductStatisticsDetailView,
                        StatisticsView, StreamCreateListView, StreamDetailView,
                        TopProductListView)

urlpatterns = [

    path('', ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('product/stats/<slug:slug>', ProductStatisticsDetailView.as_view(), name='product_stats'),
    path('top/product', TopProductListView.as_view(), name='top_product'),


    path('category-market/<slug:slug>', CategoryMarketProductView.as_view(), name='category_by_product_market'),
    path('category/<slug:slug>', ProductByCategoryListView.as_view(), name='product_by_category'),

    path('order/list', OrderListView.as_view(), name='order_list'),
    path('create/order', OrderCreateView.as_view(), name='create_order'),

    path('click-like/<int:pk>', ClickLikeView.as_view(), name='click_like'),
    path('like/product', LikeListView.as_view(), name='like_list'),

    path('market', MarketListView.as_view(), name='market'),

    path('status/success/<int:pk>', OrderSuccessDetailView.as_view(), name='status_success'),

    path('stream', StreamCreateListView.as_view(), name='stream'),
    path('stream/<int:pk>', StreamDetailView.as_view(), name='stream_detail'),

    path('statistics', StatisticsView.as_view(), name='statistics'),

    path('competition', CompetitionListView.as_view(), name='competition'),
]

