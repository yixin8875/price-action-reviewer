from unfold.admin import ModelAdmin
from unfold.decorators import action
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.db.models import Prefetch
from django.contrib import messages, admin
from django import forms
from .models import Instrument, KLine
from apps.core.chart_utils import ChartDataBuilder
from apps.technical_analysis.models import Indicator


class BatchSyncForm(forms.Form):
    market_type = forms.ChoiceField(
        label='市场类型',
        choices=[('ALL', '全部'), ('STOCK', '股票'), ('FUTURES', '期货')],
        initial='ALL'
    )
    days = forms.IntegerField(
        label='同步天数',
        initial=30,
        min_value=1,
        max_value=365
    )


@admin.register(Instrument)
class InstrumentAdmin(ModelAdmin):
    list_display = ['symbol', 'name', 'market_type', 'exchange', 'is_active', 'listing_date', 'updated_at', 'view_chart_link']
    list_filter = ['market_type', 'exchange', 'is_active']
    search_fields = ['symbol', 'name']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['sync_selected_instruments', 'calculate_selected_indicators']
    fieldsets = [
        ('基本信息', {
            'fields': ['symbol', 'name', 'market_type', 'exchange']
        }),
        ('状态信息', {
            'fields': ['is_active', 'listing_date', 'delisting_date']
        }),
        ('扩展信息', {
            'fields': ['metadata'],
            'classes': ['collapse']
        }),
        ('时间戳', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    @action(description='同步选中标的的数据')
    def sync_selected_instruments(self, request, queryset):
        from .tasks import sync_instrument_data
        count = 0
        for instrument in queryset:
            sync_instrument_data.delay(instrument.id, days=30)
            count += 1
        self.message_user(request, f'已提交 {count} 个标的的数据同步任务', messages.SUCCESS)

    @action(description='计算选中标的的技术指标')
    def calculate_selected_indicators(self, request, queryset):
        from apps.technical_analysis.tasks import calculate_indicators_task
        count = 0
        for instrument in queryset:
            calculate_indicators_task.delay(instrument.id)
            count += 1
        self.message_user(request, f'已提交 {count} 个标的的技术指标计算任务', messages.SUCCESS)

    def view_chart_link(self, obj):
        url = reverse('admin:instrument_chart', args=[obj.pk])
        return format_html('<a href="{}">查看图表</a>', url)
    view_chart_link.short_description = '图表'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_batch_sync_button'] = True
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:instrument_id>/chart/', self.admin_site.admin_view(self.chart_view), name='instrument_chart'),
            path('batch-sync/', self.admin_site.admin_view(self.batch_sync_view), name='instrument_batch_sync'),
        ]
        return custom_urls + urls

    def batch_sync_view(self, request):
        if request.method == 'POST':
            form = BatchSyncForm(request.POST)
            if form.is_valid():
                from .tasks import sync_instrument_data
                market_type = form.cleaned_data['market_type']
                days = form.cleaned_data['days']

                queryset = Instrument.objects.filter(is_active=True)
                if market_type != 'ALL':
                    queryset = queryset.filter(market_type=market_type)

                count = 0
                for instrument in queryset:
                    sync_instrument_data.delay(instrument.id, days=days)
                    count += 1

                self.message_user(request, f'已提交 {count} 个标的的数据同步任务（{days}天）', messages.SUCCESS)
                return redirect('admin:market_data_instrument_changelist')
        else:
            form = BatchSyncForm()

        context = {
            'form': form,
            'title': '批量同步数据',
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/market_data/batch_sync.html', context)

    def chart_view(self, request, instrument_id):
        instrument = Instrument.objects.get(pk=instrument_id)
        period = request.GET.get('period', '1d')

        # 获取最近100个交易日K线数据
        klines = KLine.objects.filter(
            instrument=instrument,
            period=period
        ).order_by('trade_date')[:100]

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

        # 获取技术指标数据
        indicators_data = {}
        if klines:
            kline_ids = [k.id for k in klines]
            ma_indicators = Indicator.objects.filter(
                kline_id__in=kline_ids,
                indicator_type='MA'
            ).select_related('kline')

            # 构建MA数据
            ma_dict = {5: [], 10: [], 20: []}
            for kline in klines:
                for indicator in ma_indicators:
                    if indicator.kline_id == kline.id:
                        data = indicator.indicator_data
                        for period in [5, 10, 20]:
                            key = f'MA{period}'
                            if key in data:
                                ma_dict[period].append(float(data[key]))
                            else:
                                ma_dict[period].append(None)
                        break

            for period in [5, 10, 20]:
                if ma_dict[period]:
                    indicators_data[f'MA{period}'] = ma_dict[period]

        # 构建图表配置
        chart_option = ChartDataBuilder.build_kline_option(kline_data, indicators_data)

        context = {
            'instrument': instrument,
            'chart_option': chart_option,
            'period': period,
            'title': f'{instrument.symbol} - {instrument.name} K线图',
            'opts': self.model._meta,
            'has_view_permission': True,
        }

        return render(request, 'admin/market_data/kline_chart.html', context)


@admin.register(KLine)
class KLineAdmin(ModelAdmin):
    list_display = ['instrument', 'period', 'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
    list_filter = ['period', 'trade_date']
    search_fields = ['instrument__symbol', 'instrument__name']
    date_hierarchy = 'trade_date'
    readonly_fields = ['created_at']
    list_select_related = ['instrument']

    fieldsets = [
        ('基本信息', {
            'fields': ['instrument', 'period', 'trade_date', 'trade_time']
        }),
        ('价格数据', {
            'fields': ['open_price', 'high_price', 'low_price', 'close_price']
        }),
        ('成交数据', {
            'fields': ['volume', 'amount', 'open_interest']
        }),
        ('时间戳', {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]
