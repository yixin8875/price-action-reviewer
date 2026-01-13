from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ReviewRecord, TradeLog
from .serializers import ReviewRecordSerializer, TradeLogSerializer


class ReviewRecordViewSet(viewsets.ModelViewSet):
    queryset = ReviewRecord.objects.select_related('instrument').prefetch_related('trades').all()
    serializer_class = ReviewRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['instrument', 'review_type', 'market_phase', 'trade_date', 'rating']
    search_fields = ['instrument__symbol', 'instrument__name', 'analysis_notes', 'tags']
    ordering_fields = ['trade_date', 'review_date', 'rating', 'created_at']
    ordering = ['-trade_date']


class TradeLogViewSet(viewsets.ModelViewSet):
    queryset = TradeLog.objects.select_related('instrument', 'review_record').all()
    serializer_class = TradeLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['instrument', 'trade_type', 'trade_date', 'review_record']
    search_fields = ['instrument__symbol', 'instrument__name', 'entry_reason', 'exit_reason', 'lessons_learned']
    ordering_fields = ['trade_date', 'profit_loss', 'profit_loss_pct', 'created_at']
    ordering = ['-trade_date']
