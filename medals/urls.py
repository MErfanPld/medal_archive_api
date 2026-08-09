from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    MedalViewSet,
    MedalImageViewSet,
    MedalFileViewSet,
    MedalPurchaseRecordViewSet,
    MedalValuationRecordViewSet,
)

app_name = 'medals'

router = DefaultRouter()
router.register('', MedalViewSet, basename='medal')

medal_image_list = MedalImageViewSet.as_view({'get': 'list', 'post': 'create'})
medal_image_detail = MedalImageViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})
medal_file_list = MedalFileViewSet.as_view({'get': 'list', 'post': 'create'})
medal_file_detail = MedalFileViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
medal_purchase_list = MedalPurchaseRecordViewSet.as_view({'get': 'list', 'post': 'create'})
medal_purchase_detail = MedalPurchaseRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})
medal_valuation_list = MedalValuationRecordViewSet.as_view({'get': 'list', 'post': 'create'})
medal_valuation_detail = MedalValuationRecordViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})

urlpatterns = [
    path('<int:medal_pk>/images/', medal_image_list, name='medal-image-list'),
    path('<int:medal_pk>/images/<int:pk>/', medal_image_detail, name='medal-image-detail'),
    path('<int:medal_pk>/files/', medal_file_list, name='medal-file-list'),
    path('<int:medal_pk>/files/<int:pk>/', medal_file_detail, name='medal-file-detail'),
    path('<int:medal_pk>/purchases/', medal_purchase_list, name='medal-purchase-list'),
    path('<int:medal_pk>/purchases/<int:pk>/', medal_purchase_detail, name='medal-purchase-detail'),
    path('<int:medal_pk>/valuations/', medal_valuation_list, name='medal-valuation-list'),
    path('<int:medal_pk>/valuations/<int:pk>/', medal_valuation_detail, name='medal-valuation-detail'),
] + router.urls
