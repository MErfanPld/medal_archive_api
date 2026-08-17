from django.urls import path
from rest_framework.routers import DefaultRouter

from .purchase_views import CoinPurchaseRecordViewSet, CoinValuationRecordViewSet
from .views import CoinImageViewSet, CoinViewSet

app_name = 'coins'

router = DefaultRouter()
router.register('', CoinViewSet, basename='coin')

coin_image_list = CoinImageViewSet.as_view({'get': 'list', 'post': 'create'})
coin_image_detail = CoinImageViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})
coin_purchase_list = CoinPurchaseRecordViewSet.as_view({'get': 'list', 'post': 'create'})
coin_purchase_detail = CoinPurchaseRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
coin_valuation_list = CoinValuationRecordViewSet.as_view({'get': 'list', 'post': 'create'})
coin_valuation_detail = CoinValuationRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    path('<int:coin_pk>/images/', coin_image_list, name='coin-image-list'),
    path('<int:coin_pk>/images/<int:pk>/', coin_image_detail, name='coin-image-detail'),
    path('<int:coin_pk>/purchases/', coin_purchase_list, name='coin-purchase-list'),
    path('<int:coin_pk>/purchases/<int:pk>/', coin_purchase_detail, name='coin-purchase-detail'),
    path('<int:coin_pk>/valuations/', coin_valuation_list, name='coin-valuation-list'),
    path('<int:coin_pk>/valuations/<int:pk>/', coin_valuation_detail, name='coin-valuation-detail'),
] + router.urls
