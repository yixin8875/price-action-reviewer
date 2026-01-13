from django.db import models
from apps.market_data.models import Instrument, KLine


class Indicator(models.Model):
    INDICATOR_TYPES = [
        ('MA', '移动平均线'),
        ('EMA', '指数移动平均'),
        ('MACD', 'MACD'),
        ('RSI', 'RSI'),
        ('KDJ', 'KDJ'),
        ('BOLL', '布林带'),
    ]

    kline = models.ForeignKey(KLine, on_delete=models.CASCADE, related_name='indicators')
    indicator_type = models.CharField(max_length=10, choices=INDICATOR_TYPES, db_index=True)
    indicator_data = models.JSONField(default=dict)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'technical_indicator'
        unique_together = [['kline', 'indicator_type']]
        indexes = [
            models.Index(fields=['kline', 'indicator_type']),
        ]

    def __str__(self):
        return f"{self.kline.instrument.symbol} {self.indicator_type} {self.kline.trade_date}"


class Pattern(models.Model):
    PATTERN_TYPES = [
        ('HEAD_SHOULDER', '头肩顶'),
        ('INV_HEAD_SHOULDER', '头肩底'),
        ('DOUBLE_TOP', '双顶'),
        ('DOUBLE_BOTTOM', '双底'),
        ('UPTREND', '上升趋势'),
        ('DOWNTREND', '下降趋势'),
        ('CONSOLIDATION', '盘整'),
    ]

    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='patterns')
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPES, db_index=True)
    start_date = models.DateField()
    end_date = models.DateField()
    confidence = models.IntegerField(help_text='置信度 0-100')
    key_points = models.JSONField(default=dict, help_text='关键点位数据')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'technical_pattern'
        ordering = ['-end_date']
        indexes = [
            models.Index(fields=['instrument', 'pattern_type', 'end_date']),
        ]

    def __str__(self):
        return f"{self.instrument.symbol} {self.get_pattern_type_display()} ({self.start_date} - {self.end_date})"


class SupportResistance(models.Model):
    LEVEL_TYPES = [
        ('SUPPORT', '支撑位'),
        ('RESISTANCE', '阻力位'),
    ]

    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='support_resistance')
    level_type = models.CharField(max_length=10, choices=LEVEL_TYPES, db_index=True)
    price_level = models.DecimalField(max_digits=12, decimal_places=4)
    strength = models.IntegerField(help_text='强度 1-5')
    identified_date = models.DateField()
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    touch_count = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'technical_support_resistance'
        ordering = ['-identified_date', 'price_level']
        indexes = [
            models.Index(fields=['instrument', 'is_active', 'level_type']),
        ]

    def __str__(self):
        return f"{self.instrument.symbol} {self.get_level_type_display()} {self.price_level}"
