from unfold.admin import ModelAdmin, TabularInline
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.contrib import messages, admin
from django import forms
from apps.review.models import ReviewRecord, TradeLog
from apps.market_data.models import KLine, Instrument
from apps.technical_analysis.models import Indicator, SupportResistance
from apps.core.chart_utils import ChartDataBuilder


class QuickCreateReviewForm(forms.Form):
    instrument = forms.ModelChoiceField(
        label='标的',
        queryset=Instrument.objects.filter(is_active=True)
    )
    trade_date = forms.DateField(
        label='交易日期',
        widget=admin.widgets.AdminDateWidget()
    )
    review_type = forms.ChoiceField(
        label='复盘类型',
        choices=ReviewRecord.REVIEW_TYPES
    )


class TradeLogInline(TabularInline):
    model = TradeLog
    extra = 0
    fields = ('trade_date', 'trade_type', 'entry_price', 'exit_price', 'quantity', 'profit_loss', 'profit_loss_pct')
    readonly_fields = ('profit_loss', 'profit_loss_pct')


@admin.register(ReviewRecord)
class ReviewRecordAdmin(ModelAdmin):
    list_display = ('instrument', 'trade_date', 'review_type', 'market_phase', 'rating_display', 'review_date', 'view_analysis_chart_link')
    list_filter = ('review_type', 'market_phase', 'rating', 'trade_date')
    search_fields = ('instrument__symbol', 'instrument__name', 'analysis_notes')
    date_hierarchy = 'trade_date'
    inlines = [TradeLogInline]

    fieldsets = (
        ('基本信息', {
            'fields': ('instrument', 'trade_date', 'review_type')
        }),
        ('技术分析', {
            'fields': ('market_phase', 'key_levels', 'analysis_notes', 'screenshots')
        }),
        ('评价', {
            'fields': ('rating', 'tags')
        }),
    )

    def rating_display(self, obj):
        if obj.rating:
            return format_html('⭐' * obj.rating)
        return '-'
    rating_display.short_description = '评分'

    def view_analysis_chart_link(self, obj):
        url = reverse('admin:review_analysis_chart', args=[obj.pk])
        return format_html('<a href="{}">分析图表</a>', url)
    view_analysis_chart_link.short_description = '图表'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_quick_create_button'] = True
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:review_id>/chart/', self.admin_site.admin_view(self.analysis_chart_view), name='review_analysis_chart'),
            path('quick-create/', self.admin_site.admin_view(self.quick_create_view), name='review_quick_create'),
        ]
        return custom_urls + urls

    def quick_create_view(self, request):
        if request.method == 'POST':
            form = QuickCreateReviewForm(request.POST)
            if form.is_valid():
                instrument = form.cleaned_data['instrument']
                trade_date = form.cleaned_data['trade_date']
                review_type = form.cleaned_data['review_type']

                review = ReviewRecord.objects.create(
                    instrument=instrument,
                    trade_date=trade_date,
                    review_type=review_type
                )

                self.message_user(request, f'已创建复盘记录：{instrument.symbol} - {trade_date}', messages.SUCCESS)
                return redirect('admin:review_reviewrecord_change', review.id)
        else:
            form = QuickCreateReviewForm()

        context = {
            'form': form,
            'title': '快速创建复盘',
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/review/quick_create.html', context)

    def analysis_chart_view(self, request, review_id):
        from django.db import models
        review = ReviewRecord.objects.select_related('instrument').get(pk=review_id)

        # 获取复盘日期前后30天的K线数据
        from datetime import timedelta
        start_date = review.trade_date - timedelta(days=30)
        end_date = review.trade_date + timedelta(days=30)

        klines = KLine.objects.filter(
            instrument=review.instrument,
            period='1d',
            trade_date__gte=start_date,
            trade_date__lte=end_date
        ).order_by('trade_date')

        kline_data = [
            {
                'trade_date': kline.trade_date,
                'open_price': kline.open_price,
                'high_price': kline.high_price,
                'low_price': kline.low_price,
                'close_price': kline.close_price,
                'volume': kline.volume
            }
            for kline in klines
        ]

        # 获取支撑阻力位
        support_resistance = SupportResistance.objects.filter(
            instrument=review.instrument,
            is_active=True,
            valid_from__lte=review.trade_date
        ).filter(
            models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=review.trade_date)
        )

        # 构建图表配置
        chart_option = ChartDataBuilder.build_kline_option(kline_data)

        context = {
            'review': review,
            'chart_option': chart_option,
            'support_resistance': support_resistance,
            'title': f'{review.instrument.symbol} 复盘分析图表',
            'opts': self.model._meta,
            'has_view_permission': True,
        }

        return render(request, 'admin/review/analysis_chart.html', context)


@admin.register(TradeLog)
class TradeLogAdmin(ModelAdmin):
    list_display = ('instrument', 'trade_date', 'trade_type', 'entry_price', 'exit_price', 'profit_loss_display', 'profit_loss_pct_display')
    list_filter = ('trade_type', 'trade_date')
    search_fields = ('instrument__symbol', 'instrument__name', 'entry_reason', 'exit_reason')
    date_hierarchy = 'trade_date'
    readonly_fields = ('profit_loss', 'profit_loss_pct')

    fieldsets = (
        ('交易信息', {
            'fields': ('review_record', 'instrument', 'trade_date', 'trade_type')
        }),
        ('价格信息', {
            'fields': ('entry_price', 'exit_price', 'quantity', 'stop_loss', 'take_profit')
        }),
        ('盈亏分析', {
            'fields': ('profit_loss', 'profit_loss_pct')
        }),
        ('交易笔记', {
            'fields': ('entry_reason', 'exit_reason', 'lessons_learned')
        }),
    )

    def profit_loss_display(self, obj):
        if obj.profit_loss:
            color = 'red' if obj.profit_loss > 0 else 'green'
            return format_html('<span style="color: {};">{}</span>', color, obj.profit_loss)
        return '-'
    profit_loss_display.short_description = '盈亏'

    def profit_loss_pct_display(self, obj):
        if obj.profit_loss_pct:
            color = 'red' if obj.profit_loss_pct > 0 else 'green'
            return format_html('<span style="color: {};">{}%</span>', color, obj.profit_loss_pct)
        return '-'
    profit_loss_pct_display.short_description = '盈亏百分比'

