from rest_framework import serializers
from .models import ReviewRecord, TradeLog


class TradeLogSerializer(serializers.ModelSerializer):
    instrument_symbol = serializers.CharField(source='instrument.symbol', read_only=True)
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    trade_type_display = serializers.CharField(source='get_trade_type_display', read_only=True)

    class Meta:
        model = TradeLog
        fields = '__all__'
        read_only_fields = ('profit_loss', 'profit_loss_pct', 'created_at', 'updated_at')


class ReviewRecordSerializer(serializers.ModelSerializer):
    instrument_symbol = serializers.CharField(source='instrument.symbol', read_only=True)
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    review_type_display = serializers.CharField(source='get_review_type_display', read_only=True)
    market_phase_display = serializers.CharField(source='get_market_phase_display', read_only=True)
    trades = TradeLogSerializer(many=True, read_only=True)

    class Meta:
        model = ReviewRecord
        fields = '__all__'
        read_only_fields = ('review_date', 'created_at', 'updated_at')
