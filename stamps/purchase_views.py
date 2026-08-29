from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions as drf_permissions, viewsets

from users.permissions import HasAppPermission

from .models import StampPurchaseRecord, StampValuationRecord
from .record_serializers import StampPurchaseRecordSerializer, StampValuationRecordSerializer
from .views import StampNestedMixin


@extend_schema_view(
    list=extend_schema(tags=['سوابق خرید تمبر'], summary='دریافت سوابق خرید'),
    retrieve=extend_schema(tags=['سوابق خرید تمبر'], summary='دریافت یک سابقه خرید'),
    create=extend_schema(tags=['سوابق خرید تمبر'], summary='ثبت سابقه خرید جدید'),
    destroy=extend_schema(tags=['سوابق خرید تمبر'], summary='حذف سابقه خرید'),
)
class StampPurchaseRecordViewSet(
    StampNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = StampPurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'stamps.view', 'retrieve': 'stamps.view',
        'create': 'stamps.update', 'destroy': 'stamps.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return StampPurchaseRecord.objects.none()
        return StampPurchaseRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')


@extend_schema_view(
    list=extend_schema(tags=['سوابق ارزش‌گذاری تمبر'], summary='دریافت سوابق ارزش‌گذاری'),
    retrieve=extend_schema(tags=['سوابق ارزش‌گذاری تمبر'], summary='دریافت یک سابقه ارزش‌گذاری'),
    create=extend_schema(tags=['سوابق ارزش‌گذاری تمبر'], summary='ثبت ارزش‌گذاری جدید'),
    destroy=extend_schema(tags=['سوابق ارزش‌گذاری تمبر'], summary='حذف سابقه ارزش‌گذاری'),
)
class StampValuationRecordViewSet(
    StampNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = StampValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'stamps.view', 'retrieve': 'stamps.view',
        'create': 'stamps.update', 'destroy': 'stamps.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return StampValuationRecord.objects.none()
        return StampValuationRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')
