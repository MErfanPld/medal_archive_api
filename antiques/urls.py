from django.urls import path
from rest_framework.routers import DefaultRouter

from .purchase_views import AntiquePurchaseRecordViewSet, AntiqueValuationRecordViewSet
from .views import AntiqueImageViewSet, AntiqueViewSet

app_name = 'antiques'

router = DefaultRouter()
router.register('', AntiqueViewSet, basename='antiques')

image_list = AntiqueImageViewSet.as_view({'get': 'list', 'post': 'create'})
image_detail = AntiqueImageViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})
purchase_list = AntiquePurchaseRecordViewSet.as_view({'get': 'list', 'post': 'create'})
purchase_detail = AntiquePurchaseRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
valuation_list = AntiqueValuationRecordViewSet.as_view({'get': 'list', 'post': 'create'})
valuation_detail = AntiqueValuationRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    path('<int:item_pk>/images/', image_list, name='antiques-image-list'),
    path('<int:item_pk>/images/<int:pk>/', image_detail, name='antiques-image-detail'),
    path('<int:item_pk>/purchases/', purchase_list, name='antiques-purchase-list'),
    path('<int:item_pk>/purchases/<int:pk>/', purchase_detail, name='antiques-purchase-detail'),
    path('<int:item_pk>/valuations/', valuation_list, name='antiques-valuation-list'),
    path('<int:item_pk>/valuations/<int:pk>/', valuation_detail, name='antiques-valuation-detail'),
] + router.urls
