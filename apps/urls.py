from django.urls import path

from apps.views import (ArchivedOrderListView, CancelledOrderListView,
                        CategoryMarketProductView, ClickLikeView,
                        CompetitionListView, DeliveryOrderListView,
                        LikeListView, MarketListView,
                        NewOrderListView, OrderCreateView, OrderListView,
                        OrderSuccessDetailView, ProductByCategoryListView,
                        ProductDetailView, ProductListView,
                        ProductStatisticsDetailView, ReadyOrderListView,
                        RequestListView, StatisticsView, StreamCreateListView,
                        TopProductListView, TransactionDetailView, OrderNewToReadyUpdateView,
                        AllOrderListView, CourierPageListView, OrderChangeDetailView, DeliveredOrderListView)
urlpatterns = [

    path('', ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('stream/<int:pk>', ProductDetailView.as_view(), name='stream_detail'),
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

    path('statistics', StatisticsView.as_view(), name='statistics'),

    path('competition', CompetitionListView.as_view(), name='competition'),

    path('transaction', TransactionDetailView.as_view(), name='transaction'),

    path('requests', RequestListView.as_view(), name='requests'),

    path('operator/new', NewOrderListView.as_view(), name='new_orders'),
    path('operator/ready', ReadyOrderListView.as_view(), name='ready_orders'),
    path('operator/delivery', DeliveryOrderListView.as_view(), name='delivery_orders'),
    path('operator/delivered', DeliveredOrderListView.as_view(), name='delivered_orders'),
    path('operator/cancelled', CancelledOrderListView.as_view(), name='cancelled_orders'),
    path('operator/archived', ArchivedOrderListView.as_view(), name='archived_orders'),
    path('operator/all', AllOrderListView.as_view(), name='all'),

    path('operator/order/change/<int:pk>', OrderChangeDetailView.as_view(), name='order_change'),
    path('operator/status/<int:pk>', OrderNewToReadyUpdateView.as_view(), name='order_next_status'),
    path('operator/courier/page', CourierPageListView.as_view(), name='courier_page'),
]

