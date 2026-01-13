from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
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

    @action(detail=False, methods=['post'], url_path='batch-calculate')
    def batch_calculate(self, request):
        """批量计算技术指标"""
        instrument_ids = request.data.get('instrument_ids', [])
        indicator_types = request.data.get('indicator_types', [])
        period = request.data.get('period', '1d')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        if not instrument_ids:
            return Response(
                {'error': '请选择至少一个标的'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not indicator_types:
            return Response(
                {'error': '请选择至少一个指标类型'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 调用 Celery 任务异步计算指标
        try:
            from .tasks import calculate_indicators_task
            task_count = 0
            for instrument_id in instrument_ids:
                calculate_indicators_task.delay(
                    instrument_id,
                    period=period,
                    indicator_types=indicator_types
                )
                task_count += 1

            return Response({
                'message': f'已提交 {task_count} 个标的的技术指标计算任务',
                'count': task_count,
                'indicators': indicator_types
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'提交任务失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
