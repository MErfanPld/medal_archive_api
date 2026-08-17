from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    total_medals = serializers.IntegerField()
    total_coins = serializers.IntegerField(required=False, default=0)
    total_items = serializers.IntegerField(required=False)
    countries = serializers.IntegerField()
    oldest_year = serializers.IntegerField(allow_null=True)
    newest_year = serializers.IntegerField(allow_null=True)
    value_by_currency = serializers.ListField()
    medals_by_category = serializers.ListField()
    medals_by_country_top = serializers.ListField()
    coins_by_category = serializers.ListField(required=False)
    coins_by_country_top = serializers.ListField(required=False)


class CountryReportSerializer(serializers.Serializer):
    total_medals = serializers.IntegerField()
    total_coins = serializers.IntegerField(required=False, default=0)
    items = serializers.ListField()
    medals = serializers.ListField(required=False)
    coins = serializers.ListField(required=False)


class ValueReportSerializer(serializers.Serializer):
    by_currency = serializers.ListField()
    by_country = serializers.ListField()
    by_category = serializers.ListField()
    over_time = serializers.ListField()
    note = serializers.CharField()
    medals = serializers.DictField(required=False)
    coins = serializers.DictField(required=False)


class PurchaseReportSerializer(serializers.Serializer):
    purchase_count = serializers.IntegerField()
    by_year = serializers.ListField()
    by_currency = serializers.ListField()
    by_seller = serializers.ListField()
    by_country = serializers.ListField()
    note = serializers.CharField()
    medals = serializers.DictField(required=False)
    coins = serializers.DictField(required=False)
