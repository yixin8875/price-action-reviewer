import pandas as pd
from datetime import datetime, timedelta
from django.db import transaction
from apps.market_data.models import Instrument, KLine
from .models import Indicator, Pattern, SupportResistance
from .indicators import IndicatorCalculator
from .pattern_recognition import PatternRecognizer


class TechnicalAnalysisService:
    MIN_DATA_POINTS = 60  # 最少需要的K线数据点

    @classmethod
    def calculate_and_save_indicators(cls, instrument_id, period='1d', limit=None):
        """
        计算并保存技术指标
        :param instrument_id: 标的ID
        :param period: K线周期
        :param limit: 限制计算最近N条数据
        """
        instrument = Instrument.objects.get(id=instrument_id)
        klines = KLine.objects.filter(
            instrument=instrument,
            period=period
        ).order_by('trade_date')

        if limit:
            klines = klines[:limit]

        if klines.count() < cls.MIN_DATA_POINTS:
            raise ValueError(f"数据不足，至少需要 {cls.MIN_DATA_POINTS} 个数据点")

        # 转换为DataFrame
        df = pd.DataFrame(list(klines.values(
            'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'
        )))
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # 转换为float
        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].astype(float)

        calculator = IndicatorCalculator(df)

        # 批量创建指标
        indicators_to_create = []

        # 为每个K线计算指标（滚动窗口）
        for i, kline in enumerate(klines):
            if i < cls.MIN_DATA_POINTS - 1:
                continue  # 跳过数据不足的部分

            # 使用到当前K线为止的所有数据
            window_df = df.iloc[:i+1]
            window_calculator = IndicatorCalculator(window_df)

            # 计算各类指标
            ma_data = window_calculator.calculate_ma()
            if ma_data:
                indicators_to_create.append(
                    Indicator(kline=kline, indicator_type='MA', indicator_data=ma_data)
                )

            ema_data = window_calculator.calculate_ema()
            if ema_data:
                indicators_to_create.append(
                    Indicator(kline=kline, indicator_type='EMA', indicator_data=ema_data)
                )

            macd_data = window_calculator.calculate_macd()
            if macd_data:
                indicators_to_create.append(
                    Indicator(kline=kline, indicator_type='MACD', indicator_data=macd_data)
                )

            rsi_data = window_calculator.calculate_rsi()
            if rsi_data:
                indicators_to_create.append(
                    Indicator(kline=kline, indicator_type='RSI', indicator_data=rsi_data)
                )

            kdj_data = window_calculator.calculate_kdj()
            if kdj_data:
                indicators_to_create.append(
                    Indicator(kline=kline, indicator_type='KDJ', indicator_data=kdj_data)
                )

            boll_data = window_calculator.calculate_bollinger_bands()
            if boll_data:
                indicators_to_create.append(
                    Indicator(kline=kline, indicator_type='BOLL', indicator_data=boll_data)
                )

        # 批量保存
        with transaction.atomic():
            # 删除旧指标
            Indicator.objects.filter(kline__instrument=instrument, kline__period=period).delete()
            # 批量创建新指标
            Indicator.objects.bulk_create(indicators_to_create, ignore_conflicts=True)

        return len(indicators_to_create)

    @classmethod
    def detect_and_save_patterns(cls, instrument_id, period='1d', lookback_days=120):
        """
        识别并保存形态
        :param instrument_id: 标的ID
        :param period: K线周期
        :param lookback_days: 回溯天数
        """
        instrument = Instrument.objects.get(id=instrument_id)
        start_date = datetime.now().date() - timedelta(days=lookback_days)

        klines = KLine.objects.filter(
            instrument=instrument,
            period=period,
            trade_date__gte=start_date
        ).order_by('trade_date')

        if klines.count() < cls.MIN_DATA_POINTS:
            raise ValueError(f"数据不足，至少需要 {cls.MIN_DATA_POINTS} 个数据点")

        # 转换为DataFrame
        df = pd.DataFrame(list(klines.values(
            'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'
        )))
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].astype(float)

        recognizer = PatternRecognizer(df)

        patterns_to_create = []

        # 检测趋势
        trend = recognizer.detect_trend()
        if trend:
            patterns_to_create.append(Pattern(
                instrument=instrument,
                pattern_type=trend['type'],
                start_date=df.index[0].date(),
                end_date=df.index[-1].date(),
                confidence=trend['confidence'],
                key_points={},
                description=trend['description']
            ))

        # 检测双顶双底
        double_patterns = recognizer.detect_double_top_bottom()
        for pattern in double_patterns:
            patterns_to_create.append(Pattern(
                instrument=instrument,
                pattern_type=pattern['type'],
                start_date=df.index[pattern['start_idx']].date(),
                end_date=df.index[pattern['end_idx']].date(),
                confidence=pattern['confidence'],
                key_points=pattern['key_points'],
                description=f"{pattern['type']} 形态"
            ))

        # 检测头肩形态
        head_shoulder_patterns = recognizer.detect_head_shoulder()
        for pattern in head_shoulder_patterns:
            patterns_to_create.append(Pattern(
                instrument=instrument,
                pattern_type=pattern['type'],
                start_date=df.index[pattern['start_idx']].date(),
                end_date=df.index[pattern['end_idx']].date(),
                confidence=pattern['confidence'],
                key_points=pattern['key_points'],
                description=f"{pattern['type']} 形态"
            ))

        # 批量保存
        with transaction.atomic():
            # 删除旧形态
            Pattern.objects.filter(
                instrument=instrument,
                end_date__gte=start_date
            ).delete()
            # 批量创建新形态
            Pattern.objects.bulk_create(patterns_to_create)

        return len(patterns_to_create)

    @classmethod
    def update_support_resistance(cls, instrument_id, period='1d', lookback_days=120):
        """
        更新支撑阻力位
        :param instrument_id: 标的ID
        :param period: K线周期
        :param lookback_days: 回溯天数
        """
        instrument = Instrument.objects.get(id=instrument_id)
        start_date = datetime.now().date() - timedelta(days=lookback_days)

        klines = KLine.objects.filter(
            instrument=instrument,
            period=period,
            trade_date__gte=start_date
        ).order_by('trade_date')

        if klines.count() < cls.MIN_DATA_POINTS:
            raise ValueError(f"数据不足，至少需要 {cls.MIN_DATA_POINTS} 个数据点")

        # 转换为DataFrame
        df = pd.DataFrame(list(klines.values(
            'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'
        )))
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].astype(float)

        recognizer = PatternRecognizer(df)
        levels = recognizer.detect_support_resistance()

        levels_to_create = []
        current_date = datetime.now().date()

        for level in levels:
            levels_to_create.append(SupportResistance(
                instrument=instrument,
                level_type=level['type'],
                price_level=level['price'],
                strength=level['strength'],
                identified_date=current_date,
                valid_from=current_date,
                valid_to=current_date + timedelta(days=30),
                touch_count=level['strength'],
                is_active=True,
                notes=f"自动识别的{level['type']}位"
            ))

        # 批量保存
        with transaction.atomic():
            # 将旧的支撑阻力位标记为无效
            SupportResistance.objects.filter(
                instrument=instrument,
                is_active=True
            ).update(is_active=False)

            # 批量创建新的支撑阻力位
            SupportResistance.objects.bulk_create(levels_to_create)

        return len(levels_to_create)
