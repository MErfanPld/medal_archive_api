from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions as drf_permissions, viewsets

from users.permissions import HasAppPermission

from .models import AntiquePurchaseRecord, AntiqueValuationRecord
from .record_serializers import AntiquePurchaseRecordSerializer, AntiqueValuationRecordSerializer
from .views import AntiqueNestedMixin


@extend_schema_view(
    list=extend_schema(tags=['سوابق خرید آنتیک'], summary='دریافت سوابق خرید'),
    retrieve=extend_schema(tags=['سوابق خرید آنتیک'], summary='دریافت یک سابقه خرید'),
    create=extend_schema(tags=['سوابق خرید آنتیک'], summary='ثبت سابقه خرید جدید'),
    destroy=extend_schema(tags=['سوابق خرید آنتیک'], summary='حذف سابقه خرید'),
)
class AntiquePurchaseRecordViewSet(
    AntiqueNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = AntiquePurchaseRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'antiques.view', 'retrieve': 'antiques.view',
        'create': 'antiques.update', 'destroy': 'antiques.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AntiquePurchaseRecord.objects.none()
        return AntiquePurchaseRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')


@extend_schema_view(
    list=extend_schema(tags=['سوابق ارزش‌گذاری آنتیک'], summary='دریافت سوابق ارزش‌گذاری'),
    retrieve=extend_schema(tags=['سوابق ارزش‌گذاری آنتیک'], summary='دریافت یک سابقه ارزش‌گذاری'),
    create=extend_schema(tags=['سوابق ارزش‌گذاری آنتیک'], summary='ثبت ارزش‌گذاری جدید'),
    destroy=extend_schema(tags=['سوابق ارزش‌گذاری آنتیک'], summary='حذف سابقه ارزش‌گذاری'),
)
class AntiqueValuationRecordViewSet(
    AntiqueNestedMixin,
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet,
):
    serializer_class = AntiqueValuationRecordSerializer
    permission_classes = [drf_permissions.IsAuthenticated, HasAppPermission]
    permission_map = {
        'list': 'antiques.view', 'retrieve': 'antiques.view',
        'create': 'antiques.update', 'destroy': 'antiques.update',
    }

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AntiqueValuationRecord.objects.none()
        return AntiqueValuationRecord.objects.filter(item_id=self.kwargs['item_pk']).select_related('created_by')
