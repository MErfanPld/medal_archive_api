from django.urls import path
from rest_framework.routers import DefaultRouter

from .purchase_views import SealPurchaseRecordViewSet, SealValuationRecordViewSet
from .views import SealImageViewSet, SealViewSet

app_name = 'seals'

router = DefaultRouter()
router.register('', SealViewSet, basename='seals')

image_list = SealImageViewSet.as_view({'get': 'list', 'post': 'create'})
image_detail = SealImageViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})
purchase_list = SealPurchaseRecordViewSet.as_view({'get': 'list', 'post': 'create'})
purchase_detail = SealPurchaseRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
valuation_list = SealValuationRecordViewSet.as_view({'get': 'list', 'post': 'create'})
valuation_detail = SealValuationRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    path('<int:item_pk>/images/', image_list, name='seals-image-list'),
    path('<int:item_pk>/images/<int:pk>/', image_detail, name='seals-image-detail'),
    path('<int:item_pk>/purchases/', purchase_list, name='seals-purchase-list'),
    path('<int:item_pk>/purchases/<int:pk>/', purchase_detail, name='seals-purchase-detail'),
    path('<int:item_pk>/valuations/', valuation_list, name='seals-valuation-list'),
    path('<int:item_pk>/valuations/<int:pk>/', valuation_detail, name='seals-valuation-detail'),
] + router.urls
