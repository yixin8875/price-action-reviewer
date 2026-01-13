from unfold.admin import ModelAdmin
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib import messages, admin
from django import forms
from .models import Indicator, Pattern, SupportResistance
from apps.market_data.models import Instrument


class BatchCalculateForm(forms.Form):
    instruments = forms.ModelMultipleChoiceField(
        label='选择标的',
        queryset=Instrument.objects.filter(is_active=True),
        widget=admin.widgets.FilteredSelectMultiple('标的', False)
    )
    period = forms.ChoiceField(
        label='K线周期',
        choices=[('1d', '日线'), ('1w', '周线'), ('1M', '月线')],
        initial='1d'
    )
    detect_patterns = forms.BooleanField(
        label='同时识别形态',
        required=False,
        initial=False
    )


@admin.register(Indicator)
class IndicatorAdmin(ModelAdmin):
    list_display = ['id', 'get_instrument', 'indicator_type', 'get_trade_date', 'calculated_at']
    list_filter = ['indicator_type', 'calculated_at']
    search_fields = ['kline__instrument__symbol', 'kline__instrument__name']
    readonly_fields = ['calculated_at']
    date_hierarchy = 'calculated_at'

    def get_instrument(self, obj):
        return obj.kline.instrument.symbol
    get_instrument.short_description = '标的代码'

    def get_trade_date(self, obj):
        return obj.kline.trade_date
    get_trade_date.short_description = '交易日期'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_batch_calculate_button'] = True
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('batch-calculate/', self.admin_site.admin_view(self.batch_calculate_view), name='indicator_batch_calculate'),
        ]
        return custom_urls + urls

    def batch_calculate_view(self, request):
        if request.method == 'POST':
            form = BatchCalculateForm(request.POST)
            if form.is_valid():
                from .tasks import calculate_indicators_task, detect_patterns_task
                instruments = form.cleaned_data['instruments']
                period = form.cleaned_data['period']
                detect_patterns = form.cleaned_data['detect_patterns']

                count = 0
                for instrument in instruments:
                    calculate_indicators_task.delay(instrument.id, period)
                    if detect_patterns:
                        detect_patterns_task.delay(instrument.id)
                    count += 1

                msg = f'已提交 {count} 个标的的技术指标计算任务'
                if detect_patterns:
                    msg += '（包含形态识别）'
                self.message_user(request, msg, messages.SUCCESS)
                return redirect('admin:technical_analysis_indicator_changelist')
        else:
            form = BatchCalculateForm()

        context = {
            'form': form,
            'title': '批量计算技术指标',
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/technical_analysis/batch_calculate.html', context)


@admin.register(Pattern)
class PatternAdmin(ModelAdmin):
    list_display = ['id', 'get_instrument', 'pattern_type', 'start_date', 'end_date', 'confidence', 'created_at']
    list_filter = ['pattern_type', 'confidence', 'created_at']
    search_fields = ['instrument__symbol', 'instrument__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'end_date'

    def get_instrument(self, obj):
        return obj.instrument.symbol
    get_instrument.short_description = '标的代码'


@admin.register(SupportResistance)
class SupportResistanceAdmin(ModelAdmin):
    list_display = ['id', 'get_instrument', 'level_type', 'price_level', 'strength',
                    'identified_date', 'is_active', 'touch_count']
    list_filter = ['level_type', 'strength', 'is_active', 'identified_date']
    search_fields = ['instrument__symbol', 'instrument__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'identified_date'

    def get_instrument(self, obj):
        return obj.instrument.symbol
    get_instrument.short_description = '标的代码'
