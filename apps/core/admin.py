from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from apps.market_data.models import Instrument, KLine
from apps.technical_analysis.models import Indicator
from apps.review.models import ReviewRecord, TradeLog


class DashboardAdminSite(admin.AdminSite):
    site_header = '价格行为复盘系统'
    site_title = '价格行为复盘系统'
    index_title = '系统仪表板'

    def index(self, request, extra_context=None):
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'stats': {
                'instrument_count': Instrument.objects.filter(is_active=True).count(),
                'kline_count': KLine.objects.count(),
                'indicator_count': Indicator.objects.count(),
                'review_count': ReviewRecord.objects.count(),
                'trade_count': TradeLog.objects.count(),
            },
            'recent_instruments': Instrument.objects.order_by('-updated_at')[:5],
            'recent_reviews': ReviewRecord.objects.select_related('instrument').order_by('-created_at')[:5],
        }
        return render(request, 'admin/dashboard.html', context)


dashboard_admin_site = DashboardAdminSite(name='admin')
