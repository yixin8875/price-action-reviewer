from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Instrument, KLine
from .serializers import InstrumentSerializer, KLineSerializer


class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['market_type', 'exchange', 'is_active']
    search_fields = ['symbol', 'name']
    ordering_fields = ['symbol', 'created_at', 'updated_at']
    ordering = ['symbol']


class KLineViewSet(viewsets.ModelViewSet):
    queryset = KLine.objects.select_related('instrument').all()
    serializer_class = KLineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['instrument', 'period', 'trade_date']
    search_fields = ['instrument__symbol', 'instrument__name']
    ordering_fields = ['trade_date', 'trade_time', 'created_at']
    ordering = ['-trade_date', '-trade_time']
