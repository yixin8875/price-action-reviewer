from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.market_data.models import Instrument


class ReviewRecord(models.Model):
    REVIEW_TYPES = [
        ('DAILY', '日复盘'),
        ('WEEKLY', '周复盘'),
        ('MONTHLY', '月复盘'),
    ]

    MARKET_PHASES = [
        ('UPTREND', '上升趋势'),
        ('DOWNTREND', '下降趋势'),
        ('CONSOLIDATION', '盘整'),
        ('REVERSAL', '反转'),
    ]

    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='reviews')
    review_date = models.DateField(auto_now_add=True)
    trade_date = models.DateField(db_index=True)
    review_type = models.CharField(max_length=10, choices=REVIEW_TYPES, db_index=True)
    market_phase = models.CharField(max_length=15, choices=MARKET_PHASES, db_index=True)
    key_levels = models.JSONField(default=dict, help_text='关键价位 {"support": [], "resistance": []}')
    analysis_notes = models.TextField(blank=True)
    screenshots = models.JSONField(default=list, help_text='截图路径列表')
    tags = models.CharField(max_length=200, blank=True, help_text='标签，逗号分隔')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text='评分 1-5星'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'review_record'
        ordering = ['-trade_date']
        indexes = [
            models.Index(fields=['instrument', 'trade_date']),
            models.Index(fields=['review_type', 'trade_date']),
        ]

    def __str__(self):
        return f"{self.instrument.symbol} {self.trade_date} {self.get_review_type_display()}"


class TradeLog(models.Model):
    TRADE_TYPES = [
        ('LONG', '做多'),
        ('SHORT', '做空'),
    ]

    review_record = models.ForeignKey(
        ReviewRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trades'
    )
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='trades')
    trade_date = models.DateField(db_index=True)
    trade_type = models.CharField(max_length=5, choices=TRADE_TYPES, db_index=True)
    entry_price = models.DecimalField(max_digits=12, decimal_places=4)
    exit_price = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    stop_loss = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    profit_loss_pct = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    entry_reason = models.TextField(blank=True)
    exit_reason = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'review_trade_log'
        ordering = ['-trade_date']
        indexes = [
            models.Index(fields=['instrument', 'trade_date']),
            models.Index(fields=['trade_type', 'trade_date']),
        ]

    def __str__(self):
        return f"{self.instrument.symbol} {self.get_trade_type_display()} {self.trade_date}"

    def save(self, *args, **kwargs):
        if self.exit_price:
            if self.trade_type == 'LONG':
                self.profit_loss = (self.exit_price - self.entry_price) * self.quantity
            else:  # SHORT
                self.profit_loss = (self.entry_price - self.exit_price) * self.quantity

            cost_base = self.entry_price * self.quantity
            if cost_base:
                self.profit_loss_pct = (self.profit_loss / cost_base) * Decimal('100')

        super().save(*args, **kwargs)
