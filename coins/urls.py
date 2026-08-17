from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CoinImageViewSet, CoinViewSet

app_name = 'coins'

router = DefaultRouter()
router.register('', CoinViewSet, basename='coin')

coin_image_list = CoinImageViewSet.as_view({'get': 'list', 'post': 'create'})
coin_image_detail = CoinImageViewSet.as_view({
    'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
})

urlpatterns = [
    path('<int:coin_pk>/images/', coin_image_list, name='coin-image-list'),
    path('<int:coin_pk>/images/<int:pk>/', coin_image_detail, name='coin-image-detail'),
] + router.urls
