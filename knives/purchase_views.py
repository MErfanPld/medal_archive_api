from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions as drf_permissions, viewsets

from users.permissions import HasAppPermission

from .models import KnifePurchaseRecord, KnifeValuationRecord
from .record_serializers import KnifePurchaseRecordSerializer, KnifeValuationRecordSerializer
from .views import KnifeNestedMixin


@extend_schema_view(
    list=extend_schema(tags=['سوابق خرید چاقو'], summary='دریافت سوابق خرید'),
    retrieve=extend_schema(tags=['سوابق خرید چاقو'], summary='دریافت یک سابقه خرید'),
    create=extend_schema(tags=['سوابق خرید چاقو'], summary='ثبت سابقه خرید جدید'),
    destroy=extend_schema(tags=['سوابق خرید چاقو'], summary='حذف سابقه خرید'),
)
class KnifePurchaseRecordViewSet(
    KnifeNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = KnifePurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'knives.view', 'retrieve': 'knives.view',
        'create': 'knives.update', 'destroy': 'knives.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return KnifePurchaseRecord.objects.none()
        return KnifePurchaseRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')


@extend_schema_view(
    list=extend_schema(tags=['سوابق ارزش‌گذاری چاقو'], summary='دریافت سوابق ارزش‌گذاری'),
    retrieve=extend_schema(tags=['سوابق ارزش‌گذاری چاقو'], summary='دریافت یک سابقه ارزش‌گذاری'),
    create=extend_schema(tags=['سوابق ارزش‌گذاری چاقو'], summary='ثبت ارزش‌گذاری جدید'),
    destroy=extend_schema(tags=['سوابق ارزش‌گذاری چاقو'], summary='حذف سابقه ارزش‌گذاری'),
)
class KnifeValuationRecordViewSet(
    KnifeNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = KnifeValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'knives.view', 'retrieve': 'knives.view',
        'create': 'knives.update', 'destroy': 'knives.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return KnifeValuationRecord.objects.none()
        return KnifeValuationRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')
