from django.db.models import Count, Sum, Avg, Q
from decimal import Decimal
from datetime import date
from apps.review.models import ReviewRecord, TradeLog
from apps.market_data.models import Instrument, KLine
from apps.technical_analysis.models import Pattern, SupportResistance, Indicator


class ReviewService:
    @staticmethod
    def create_review_with_analysis(instrument_id, trade_date, review_type='DAILY'):
        """创建复盘记录并自动关联技术分析"""
        instrument = Instrument.objects.get(id=instrument_id)

        # 获取当日K线数据
        kline = KLine.objects.filter(
            instrument=instrument,
            period='1d',
            trade_date=trade_date
        ).first()

        # 获取支撑阻力位
        key_levels = {'support': [], 'resistance': []}
        sr_levels = SupportResistance.objects.filter(
            instrument=instrument,
            is_active=True,
            valid_from__lte=trade_date
        ).filter(Q(valid_to__isnull=True) | Q(valid_to__gte=trade_date))

        for sr in sr_levels:
            price = float(sr.price_level)
            if sr.level_type == 'SUPPORT':
                key_levels['support'].append(price)
            else:
                key_levels['resistance'].append(price)

        key_levels['support'].sort()
        key_levels['resistance'].sort()

        # 自动判断市场阶段
        market_phase = ReviewService._determine_market_phase(instrument, trade_date)

        # 创建复盘记录
        review = ReviewRecord.objects.create(
            instrument=instrument,
            trade_date=trade_date,
            review_type=review_type,
            market_phase=market_phase,
            key_levels=key_levels
        )

        return review

    @staticmethod
    def _determine_market_phase(instrument, trade_date):
        """自动判断市场阶段"""
        # 查找最近的形态识别结果
        pattern = Pattern.objects.filter(
            instrument=instrument,
            end_date__lte=trade_date
        ).order_by('-end_date').first()

        if pattern:
            if pattern.pattern_type in ['UPTREND']:
                return 'UPTREND'
            elif pattern.pattern_type in ['DOWNTREND']:
                return 'DOWNTREND'
            elif pattern.pattern_type in ['CONSOLIDATION']:
                return 'CONSOLIDATION'
            elif pattern.pattern_type in ['HEAD_SHOULDER', 'DOUBLE_TOP', 'INV_HEAD_SHOULDER', 'DOUBLE_BOTTOM']:
                return 'REVERSAL'

        # 如果没有形态数据，基于价格与移动平均线关系判断
        kline = KLine.objects.filter(
            instrument=instrument,
            period='1d',
            trade_date=trade_date
        ).first()

        if kline:
            indicator = Indicator.objects.filter(
                kline=kline,
                indicator_type='MA'
            ).first()

            if indicator and indicator.indicator_data:
                ma20 = indicator.indicator_data.get('MA20')
                ma60 = indicator.indicator_data.get('MA60')

                if ma20 and ma60:
                    close_price = float(kline.close_price)
                    if close_price > ma20 > ma60:
                        return 'UPTREND'
                    elif close_price < ma20 < ma60:
                        return 'DOWNTREND'

        return 'CONSOLIDATION'

    @staticmethod
    def get_trade_statistics(start_date=None, end_date=None, instrument_id=None):
        """获取交易统计"""
        trades = TradeLog.objects.filter(exit_price__isnull=False)

        if start_date:
            trades = trades.filter(trade_date__gte=start_date)
        if end_date:
            trades = trades.filter(trade_date__lte=end_date)
        if instrument_id:
            trades = trades.filter(instrument_id=instrument_id)

        total_trades = trades.count()
        if total_trades == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_loss_ratio': 0,
                'total_profit_loss': 0,
                'avg_profit': 0,
                'avg_loss': 0,
            }

        winning_trades = trades.filter(profit_loss__gt=0)
        losing_trades = trades.filter(profit_loss__lt=0)

        win_count = winning_trades.count()
        loss_count = losing_trades.count()

        total_profit = winning_trades.aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0')
        total_loss = abs(losing_trades.aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0'))

        avg_profit = winning_trades.aggregate(Avg('profit_loss'))['profit_loss__avg'] or Decimal('0')
        avg_loss = abs(losing_trades.aggregate(Avg('profit_loss'))['profit_loss__avg'] or Decimal('0'))

        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        profit_loss_ratio = (avg_profit / avg_loss) if avg_loss > 0 else 0

        total_pl = trades.aggregate(Sum('profit_loss'))['profit_loss__sum'] or Decimal('0')

        return {
            'total_trades': total_trades,
            'win_count': win_count,
            'loss_count': loss_count,
            'win_rate': round(win_rate, 2),
            'profit_loss_ratio': round(float(profit_loss_ratio), 2),
            'total_profit_loss': float(total_pl),
            'avg_profit': float(avg_profit),
            'avg_loss': float(avg_loss),
        }

    @staticmethod
    def get_review_summary(instrument_id):
        """获取标的复盘摘要"""
        reviews = ReviewRecord.objects.filter(instrument_id=instrument_id)

        total_reviews = reviews.count()
        if total_reviews == 0:
            return {
                'total_reviews': 0,
                'avg_rating': 0,
                'common_tags': [],
            }

        avg_rating = reviews.filter(rating__isnull=False).aggregate(Avg('rating'))['rating__avg'] or 0

        # 统计标签
        all_tags = []
        for review in reviews.exclude(tags=''):
            tags = [tag.strip() for tag in review.tags.split(',') if tag.strip()]
            all_tags.extend(tags)

        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'total_reviews': total_reviews,
            'avg_rating': round(avg_rating, 2),
            'common_tags': [{'tag': tag, 'count': count} for tag, count in common_tags],
        }
