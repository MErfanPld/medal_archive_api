from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    total_medals = serializers.IntegerField()
    countries = serializers.IntegerField()
    oldest_year = serializers.IntegerField(allow_null=True)
    newest_year = serializers.IntegerField(allow_null=True)
    value_by_currency = serializers.ListField()
    medals_by_category = serializers.ListField()
    medals_by_country_top = serializers.ListField()


class CountryReportSerializer(serializers.Serializer):
    total_medals = serializers.IntegerField()
    items = serializers.ListField()


class ValueReportSerializer(serializers.Serializer):
    by_currency = serializers.ListField()
    by_country = serializers.ListField()
    by_category = serializers.ListField()
    over_time = serializers.ListField()
    note = serializers.CharField()


class PurchaseReportSerializer(serializers.Serializer):
    purchase_count = serializers.IntegerField()
    by_year = serializers.ListField()
    by_currency = serializers.ListField()
    by_seller = serializers.ListField()
    by_country = serializers.ListField()
    note = serializers.CharField()
