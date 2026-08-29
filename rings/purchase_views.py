from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions as drf_permissions, viewsets

from users.permissions import HasAppPermission

from .models import RingPurchaseRecord, RingValuationRecord
from .record_serializers import RingPurchaseRecordSerializer, RingValuationRecordSerializer
from .views import RingNestedMixin


@extend_schema_view(
    list=extend_schema(tags=['سوابق خرید انگشتر'], summary='دریافت سوابق خرید'),
    retrieve=extend_schema(tags=['سوابق خرید انگشتر'], summary='دریافت یک سابقه خرید'),
    create=extend_schema(tags=['سوابق خرید انگشتر'], summary='ثبت سابقه خرید جدید'),
    destroy=extend_schema(tags=['سوابق خرید انگشتر'], summary='حذف سابقه خرید'),
)
class RingPurchaseRecordViewSet(
    RingNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = RingPurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'rings.view', 'retrieve': 'rings.view',
        'create': 'rings.update', 'destroy': 'rings.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return RingPurchaseRecord.objects.none()
        return RingPurchaseRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')


@extend_schema_view(
    list=extend_schema(tags=['سوابق ارزش‌گذاری انگشتر'], summary='دریافت سوابق ارزش‌گذاری'),
    retrieve=extend_schema(tags=['سوابق ارزش‌گذاری انگشتر'], summary='دریافت یک سابقه ارزش‌گذاری'),
    create=extend_schema(tags=['سوابق ارزش‌گذاری انگشتر'], summary='ثبت ارزش‌گذاری جدید'),
    destroy=extend_schema(tags=['سوابق ارزش‌گذاری انگشتر'], summary='حذف سابقه ارزش‌گذاری'),
)
class RingValuationRecordViewSet(
    RingNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = RingValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'rings.view', 'retrieve': 'rings.view',
        'create': 'rings.update', 'destroy': 'rings.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return RingValuationRecord.objects.none()
        return RingValuationRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')
