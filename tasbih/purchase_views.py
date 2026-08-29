from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions as drf_permissions, viewsets

from users.permissions import HasAppPermission

from .models import TasbihPurchaseRecord, TasbihValuationRecord
from .record_serializers import TasbihPurchaseRecordSerializer, TasbihValuationRecordSerializer
from .views import TasbihNestedMixin


@extend_schema_view(
    list=extend_schema(tags=['سوابق خرید تسبیح'], summary='دریافت سوابق خرید'),
    retrieve=extend_schema(tags=['سوابق خرید تسبیح'], summary='دریافت یک سابقه خرید'),
    create=extend_schema(tags=['سوابق خرید تسبیح'], summary='ثبت سابقه خرید جدید'),
    destroy=extend_schema(tags=['سوابق خرید تسبیح'], summary='حذف سابقه خرید'),
)
class TasbihPurchaseRecordViewSet(
    TasbihNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = TasbihPurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'tasbih.view', 'retrieve': 'tasbih.view',
        'create': 'tasbih.update', 'destroy': 'tasbih.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return TasbihPurchaseRecord.objects.none()
        return TasbihPurchaseRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')


@extend_schema_view(
    list=extend_schema(tags=['سوابق ارزش‌گذاری تسبیح'], summary='دریافت سوابق ارزش‌گذاری'),
    retrieve=extend_schema(tags=['سوابق ارزش‌گذاری تسبیح'], summary='دریافت یک سابقه ارزش‌گذاری'),
    create=extend_schema(tags=['سوابق ارزش‌گذاری تسبیح'], summary='ثبت ارزش‌گذاری جدید'),
    destroy=extend_schema(tags=['سوابق ارزش‌گذاری تسبیح'], summary='حذف سابقه ارزش‌گذاری'),
)
class TasbihValuationRecordViewSet(
    TasbihNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = TasbihValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'tasbih.view', 'retrieve': 'tasbih.view',
        'create': 'tasbih.update', 'destroy': 'tasbih.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return TasbihValuationRecord.objects.none()
        return TasbihValuationRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')
