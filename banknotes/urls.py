from django.urls import path
from rest_framework.routers import DefaultRouter

from .purchase_views import BanknotePurchaseRecordViewSet, BanknoteValuationRecordViewSet
from .views import BanknoteImageViewSet, BanknoteViewSet

app_name = 'banknotes'

router = DefaultRouter()
router.register('', BanknoteViewSet, basename='banknotes')

image_list = BanknoteImageViewSet.as_view({'get': 'list', 'post': 'create'})
image_detail = BanknoteImageViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})
purchase_list = BanknotePurchaseRecordViewSet.as_view({'get': 'list', 'post': 'create'})
purchase_detail = BanknotePurchaseRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
valuation_list = BanknoteValuationRecordViewSet.as_view({'get': 'list', 'post': 'create'})
valuation_detail = BanknoteValuationRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    path('<int:item_pk>/images/', image_list, name='banknotes-image-list'),
    path('<int:item_pk>/images/<int:pk>/', image_detail, name='banknotes-image-detail'),
    path('<int:item_pk>/purchases/', purchase_list, name='banknotes-purchase-list'),
    path('<int:item_pk>/purchases/<int:pk>/', purchase_detail, name='banknotes-purchase-detail'),
    path('<int:item_pk>/valuations/', valuation_list, name='banknotes-valuation-list'),
    path('<int:item_pk>/valuations/<int:pk>/', valuation_detail, name='banknotes-valuation-detail'),
] + router.urls
