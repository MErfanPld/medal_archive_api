from django.urls import path
from rest_framework.routers import DefaultRouter

from .purchase_views import StampPurchaseRecordViewSet, StampValuationRecordViewSet
from .views import StampImageViewSet, StampViewSet

app_name = 'stamps'

router = DefaultRouter()
router.register('', StampViewSet, basename='stamps')

image_list = StampImageViewSet.as_view({'get': 'list', 'post': 'create'})
image_detail = StampImageViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})
purchase_list = StampPurchaseRecordViewSet.as_view({'get': 'list', 'post': 'create'})
purchase_detail = StampPurchaseRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
valuation_list = StampValuationRecordViewSet.as_view({'get': 'list', 'post': 'create'})
valuation_detail = StampValuationRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    path('<int:item_pk>/images/', image_list, name='stamps-image-list'),
    path('<int:item_pk>/images/<int:pk>/', image_detail, name='stamps-image-detail'),
    path('<int:item_pk>/purchases/', purchase_list, name='stamps-purchase-list'),
    path('<int:item_pk>/purchases/<int:pk>/', purchase_detail, name='stamps-purchase-detail'),
    path('<int:item_pk>/valuations/', valuation_list, name='stamps-valuation-list'),
    path('<int:item_pk>/valuations/<int:pk>/', valuation_detail, name='stamps-valuation-detail'),
] + router.urls
