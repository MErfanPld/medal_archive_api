from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions as drf_permissions, viewsets

from users.permissions import HasAppPermission

from .models import BanknotePurchaseRecord, BanknoteValuationRecord
from .record_serializers import BanknotePurchaseRecordSerializer, BanknoteValuationRecordSerializer
from .views import BanknoteNestedMixin


@extend_schema_view(
    list=extend_schema(tags=['سوابق خرید اسکناس'], summary='دریافت سوابق خرید'),
    retrieve=extend_schema(tags=['سوابق خرید اسکناس'], summary='دریافت یک سابقه خرید'),
    create=extend_schema(tags=['سوابق خرید اسکناس'], summary='ثبت سابقه خرید جدید'),
    destroy=extend_schema(tags=['سوابق خرید اسکناس'], summary='حذف سابقه خرید'),
)
class BanknotePurchaseRecordViewSet(
    BanknoteNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = BanknotePurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'banknotes.view', 'retrieve': 'banknotes.view',
        'create': 'banknotes.update', 'destroy': 'banknotes.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BanknotePurchaseRecord.objects.none()
        return BanknotePurchaseRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')


@extend_schema_view(
    list=extend_schema(tags=['سوابق ارزش‌گذاری اسکناس'], summary='دریافت سوابق ارزش‌گذاری'),
    retrieve=extend_schema(tags=['سوابق ارزش‌گذاری اسکناس'], summary='دریافت یک سابقه ارزش‌گذاری'),
    create=extend_schema(tags=['سوابق ارزش‌گذاری اسکناس'], summary='ثبت ارزش‌گذاری جدید'),
    destroy=extend_schema(tags=['سوابق ارزش‌گذاری اسکناس'], summary='حذف سابقه ارزش‌گذاری'),
)
class BanknoteValuationRecordViewSet(
    BanknoteNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = BanknoteValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'banknotes.view', 'retrieve': 'banknotes.view',
        'create': 'banknotes.update', 'destroy': 'banknotes.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BanknoteValuationRecord.objects.none()
        return BanknoteValuationRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')
