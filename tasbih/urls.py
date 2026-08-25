from django.urls import path
from rest_framework.routers import DefaultRouter

from .purchase_views import TasbihPurchaseRecordViewSet, TasbihValuationRecordViewSet
from .views import TasbihImageViewSet, TasbihViewSet

app_name = 'tasbih'

router = DefaultRouter()
router.register('', TasbihViewSet, basename='tasbih')

image_list = TasbihImageViewSet.as_view({'get': 'list', 'post': 'create'})
image_detail = TasbihImageViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})
purchase_list = TasbihPurchaseRecordViewSet.as_view({'get': 'list', 'post': 'create'})
purchase_detail = TasbihPurchaseRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
valuation_list = TasbihValuationRecordViewSet.as_view({'get': 'list', 'post': 'create'})
valuation_detail = TasbihValuationRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    path('<int:item_pk>/images/', image_list, name='tasbih-image-list'),
    path('<int:item_pk>/images/<int:pk>/', image_detail, name='tasbih-image-detail'),
    path('<int:item_pk>/purchases/', purchase_list, name='tasbih-purchase-list'),
    path('<int:item_pk>/purchases/<int:pk>/', purchase_detail, name='tasbih-purchase-detail'),
    path('<int:item_pk>/valuations/', valuation_list, name='tasbih-valuation-list'),
    path('<int:item_pk>/valuations/<int:pk>/', valuation_detail, name='tasbih-valuation-detail'),
] + router.urls
