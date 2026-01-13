from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
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

    @action(detail=False, methods=['post'], url_path='batch-import')
    def batch_import(self, request):
        """批量导入K线数据"""
        instrument_ids = request.data.get('instrument_ids', [])
        days = request.data.get('days', 30)
        market_type = request.data.get('market_type')

        # 转换 market_type 为大写
        if market_type:
            market_type = market_type.upper()

        if not instrument_ids and not market_type:
            return Response(
                {'error': '请选择标的或市场类型'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 如果没有指定标的，根据市场类型获取所有活跃标的
        if not instrument_ids:
            queryset = Instrument.objects.filter(is_active=True)
            if market_type and market_type != 'ALL':
                queryset = queryset.filter(market_type=market_type)
            instrument_ids = list(queryset.values_list('id', flat=True))

        # 调用 Celery 任务异步同步数据
        try:
            from .tasks import sync_instrument_data
            task_count = 0
            for instrument_id in instrument_ids:
                sync_instrument_data.delay(instrument_id, days=days)
                task_count += 1

            return Response({
                'message': f'已提交 {task_count} 个标的的数据同步任务',
                'count': task_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'提交任务失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
