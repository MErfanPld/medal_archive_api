from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions as drf_permissions, viewsets

from users.permissions import HasAppPermission

from .models import SealPurchaseRecord, SealValuationRecord
from .record_serializers import SealPurchaseRecordSerializer, SealValuationRecordSerializer
from .views import SealNestedMixin


@extend_schema_view(
    list=extend_schema(tags=['سوابق خرید مهر'], summary='دریافت سوابق خرید'),
    retrieve=extend_schema(tags=['سوابق خرید مهر'], summary='دریافت یک سابقه خرید'),
    create=extend_schema(tags=['سوابق خرید مهر'], summary='ثبت سابقه خرید جدید'),
    destroy=extend_schema(tags=['سوابق خرید مهر'], summary='حذف سابقه خرید'),
)
class SealPurchaseRecordViewSet(
    SealNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = SealPurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'seals.view', 'retrieve': 'seals.view',
        'create': 'seals.update', 'destroy': 'seals.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SealPurchaseRecord.objects.none()
        return SealPurchaseRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')


@extend_schema_view(
    list=extend_schema(tags=['سوابق ارزش‌گذاری مهر'], summary='دریافت سوابق ارزش‌گذاری'),
    retrieve=extend_schema(tags=['سوابق ارزش‌گذاری مهر'], summary='دریافت یک سابقه ارزش‌گذاری'),
    create=extend_schema(tags=['سوابق ارزش‌گذاری مهر'], summary='ثبت ارزش‌گذاری جدید'),
    destroy=extend_schema(tags=['سوابق ارزش‌گذاری مهر'], summary='حذف سابقه ارزش‌گذاری'),
)
class SealValuationRecordViewSet(
    SealNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = SealValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'seals.view', 'retrieve': 'seals.view',
        'create': 'seals.update', 'destroy': 'seals.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SealValuationRecord.objects.none()
        return SealValuationRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')
