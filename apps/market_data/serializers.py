from rest_framework import serializers
from .models import Instrument, KLine


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class KLineSerializer(serializers.ModelSerializer):
    instrument_symbol = serializers.CharField(source='instrument.symbol', read_only=True)
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)

    class Meta:
        model = KLine
        fields = '__all__'
        read_only_fields = ('created_at',)
