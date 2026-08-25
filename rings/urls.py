from django.urls import path
from rest_framework.routers import DefaultRouter

from .purchase_views import RingPurchaseRecordViewSet, RingValuationRecordViewSet
from .views import RingImageViewSet, RingViewSet

app_name = 'rings'

router = DefaultRouter()
router.register('', RingViewSet, basename='rings')

image_list = RingImageViewSet.as_view({'get': 'list', 'post': 'create'})
image_detail = RingImageViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})
purchase_list = RingPurchaseRecordViewSet.as_view({'get': 'list', 'post': 'create'})
purchase_detail = RingPurchaseRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
valuation_list = RingValuationRecordViewSet.as_view({'get': 'list', 'post': 'create'})
valuation_detail = RingValuationRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    path('<int:item_pk>/images/', image_list, name='rings-image-list'),
    path('<int:item_pk>/images/<int:pk>/', image_detail, name='rings-image-detail'),
    path('<int:item_pk>/purchases/', purchase_list, name='rings-purchase-list'),
    path('<int:item_pk>/purchases/<int:pk>/', purchase_detail, name='rings-purchase-detail'),
    path('<int:item_pk>/valuations/', valuation_list, name='rings-valuation-list'),
    path('<int:item_pk>/valuations/<int:pk>/', valuation_detail, name='rings-valuation-detail'),
] + router.urls
