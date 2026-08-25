from django.urls import path
from rest_framework.routers import DefaultRouter

from .purchase_views import KnifePurchaseRecordViewSet, KnifeValuationRecordViewSet
from .views import KnifeImageViewSet, KnifeViewSet

app_name = 'knives'

router = DefaultRouter()
router.register('', KnifeViewSet, basename='knives')

image_list = KnifeImageViewSet.as_view({'get': 'list', 'post': 'create'})
image_detail = KnifeImageViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})
purchase_list = KnifePurchaseRecordViewSet.as_view({'get': 'list', 'post': 'create'})
purchase_detail = KnifePurchaseRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
valuation_list = KnifeValuationRecordViewSet.as_view({'get': 'list', 'post': 'create'})
valuation_detail = KnifeValuationRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    path('<int:item_pk>/images/', image_list, name='knives-image-list'),
    path('<int:item_pk>/images/<int:pk>/', image_detail, name='knives-image-detail'),
    path('<int:item_pk>/purchases/', purchase_list, name='knives-purchase-list'),
    path('<int:item_pk>/purchases/<int:pk>/', purchase_detail, name='knives-purchase-detail'),
    path('<int:item_pk>/valuations/', valuation_list, name='knives-valuation-list'),
    path('<int:item_pk>/valuations/<int:pk>/', valuation_detail, name='knives-valuation-detail'),
] + router.urls
