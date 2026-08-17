"""Nested purchase & valuation viewsets for coins."""
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions as drf_permissions, viewsets

from users.permissions import HasAppPermission

from .models import Coin, CoinPurchaseRecord, CoinValuationRecord
from .record_serializers import CoinPurchaseRecordSerializer, CoinValuationRecordSerializer


class CoinNestedMixin:
    coin_url_kwarg = 'coin_pk'

    def get_coin(self):
        return get_object_or_404(Coin, pk=self.kwargs[self.coin_url_kwarg])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['coin'] = self.get_coin()
        return ctx


@extend_schema_view(
    list=extend_schema(tags=['سوابق خرید سکه و پول'], summary='دریافت سوابق خرید'),
    retrieve=extend_schema(tags=['سوابق خرید سکه و پول'], summary='دریافت یک سابقه خرید'),
    create=extend_schema(tags=['سوابق خرید سکه و پول'], summary='ثبت سابقه خرید جدید'),
    destroy=extend_schema(tags=['سوابق خرید سکه و پول'], summary='حذف سابقه خرید'),
)
class CoinPurchaseRecordViewSet(
    CoinNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = CoinPurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'coins.view', 'retrieve': 'coins.view',
        'create': 'coins.update', 'destroy': 'coins.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CoinPurchaseRecord.objects.none()
        return CoinPurchaseRecord.objects.filter(
            coin_id=self.kwargs['coin_pk']
        ).select_related('created_by')


@extend_schema_view(
    list=extend_schema(tags=['سوابق ارزش‌گذاری سکه و پول'], summary='دریافت سوابق ارزش‌گذاری'),
    retrieve=extend_schema(tags=['سوابق ارزش‌گذاری سکه و پول'], summary='دریافت یک سابقه ارزش‌گذاری'),
    create=extend_schema(tags=['سوابق ارزش‌گذاری سکه و پول'], summary='ثبت ارزش‌گذاری جدید'),
    destroy=extend_schema(tags=['سوابق ارزش‌گذاری سکه و پول'], summary='حذف سابقه ارزش‌گذاری'),
)
class CoinValuationRecordViewSet(
    CoinNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = CoinValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'coins.view', 'retrieve': 'coins.view',
        'create': 'coins.update', 'destroy': 'coins.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CoinValuationRecord.objects.none()
        return CoinValuationRecord.objects.filter(
            coin_id=self.kwargs['coin_pk']
        ).select_related('created_by')
