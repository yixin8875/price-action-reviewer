from django.db import models
from decimal import Decimal


class Instrument(models.Model):
    MARKET_TYPES = [
        ('STOCK', '股票'),
        ('FUTURES', '期货'),
    ]

    EXCHANGES = [
        ('SSE', '上海证券交易所'),
        ('SZSE', '深圳证券交易所'),
        ('CFFEX', '中国金融期货交易所'),
        ('SHFE', '上海期货交易所'),
        ('DCE', '大连商品交易所'),
        ('CZCE', '郑州商品交易所'),
    ]

    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    market_type = models.CharField(max_length=10, choices=MARKET_TYPES, db_index=True)
    exchange = models.CharField(max_length=10, choices=EXCHANGES)
    listing_date = models.DateField(null=True, blank=True)
    delisting_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'market_instrument'
        ordering = ['symbol']

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class KLine(models.Model):
    PERIODS = [
        ('1m', '1分钟'),
        ('5m', '5分钟'),
        ('15m', '15分钟'),
        ('30m', '30分钟'),
        ('1h', '1小时'),
        ('1d', '日线'),
        ('1w', '周线'),
        ('1M', '月线'),
    ]

    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='klines')
    period = models.CharField(max_length=5, choices=PERIODS, db_index=True)
    trade_date = models.DateField(db_index=True)
    trade_time = models.TimeField(null=True, blank=True)
    open_price = models.DecimalField(max_digits=12, decimal_places=4)
    high_price = models.DecimalField(max_digits=12, decimal_places=4)
    low_price = models.DecimalField(max_digits=12, decimal_places=4)
    close_price = models.DecimalField(max_digits=12, decimal_places=4)
    volume = models.BigIntegerField()
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    open_interest = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'market_kline'
        ordering = ['-trade_date', '-trade_time']
        unique_together = [['instrument', 'period', 'trade_date', 'trade_time']]
        indexes = [
            models.Index(fields=['instrument', 'period', 'trade_date']),
        ]

    def __str__(self):
        return f"{self.instrument.symbol} {self.period} {self.trade_date}"
