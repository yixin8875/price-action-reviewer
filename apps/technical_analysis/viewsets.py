from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Indicator, Pattern, SupportResistance
from .serializers import IndicatorSerializer, PatternSerializer, SupportResistanceSerializer


class IndicatorViewSet(viewsets.ModelViewSet):
    queryset = Indicator.objects.select_related('kline__instrument').all()
    serializer_class = IndicatorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['kline', 'indicator_type']
    search_fields = ['kline__instrument__symbol', 'kline__instrument__name']
    ordering_fields = ['calculated_at']
    ordering = ['-calculated_at']


class PatternViewSet(viewsets.ModelViewSet):
    queryset = Pattern.objects.select_related('instrument').all()
    serializer_class = PatternSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['instrument', 'pattern_type', 'start_date', 'end_date']
    search_fields = ['instrument__symbol', 'instrument__name', 'description']
    ordering_fields = ['start_date', 'end_date', 'confidence', 'created_at']
    ordering = ['-end_date']


class SupportResistanceViewSet(viewsets.ModelViewSet):
    queryset = SupportResistance.objects.select_related('instrument').all()
    serializer_class = SupportResistanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['instrument', 'level_type', 'is_active', 'identified_date']
    search_fields = ['instrument__symbol', 'instrument__name', 'notes']
    ordering_fields = ['identified_date', 'price_level', 'strength', 'created_at']
    ordering = ['-identified_date', 'price_level']
