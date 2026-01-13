from rest_framework import serializers
from .models import Indicator, Pattern, SupportResistance


class IndicatorSerializer(serializers.ModelSerializer):
    instrument_symbol = serializers.CharField(source='kline.instrument.symbol', read_only=True)
    trade_date = serializers.DateField(source='kline.trade_date', read_only=True)

    class Meta:
        model = Indicator
        fields = '__all__'
        read_only_fields = ('calculated_at',)


class PatternSerializer(serializers.ModelSerializer):
    instrument_symbol = serializers.CharField(source='instrument.symbol', read_only=True)
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    pattern_type_display = serializers.CharField(source='get_pattern_type_display', read_only=True)

    class Meta:
        model = Pattern
        fields = '__all__'
        read_only_fields = ('created_at',)


class SupportResistanceSerializer(serializers.ModelSerializer):
    instrument_symbol = serializers.CharField(source='instrument.symbol', read_only=True)
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    level_type_display = serializers.CharField(source='get_level_type_display', read_only=True)

    class Meta:
        model = SupportResistance
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
