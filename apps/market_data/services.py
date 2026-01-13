from django.db import transaction
from datetime import datetime, timedelta
import logging
from .models import Instrument, KLine
from .data_fetcher import AkshareDataFetcher

logger = logging.getLogger(__name__)


class MarketDataService:
    """市场数据服务"""

    def __init__(self):
        self.fetcher = AkshareDataFetcher()

    def import_instrument(self, symbol, market_type, **kwargs):
        """导入标的信息"""
        try:
            instrument, created = Instrument.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'market_type': market_type,
                    'name': kwargs.get('name', symbol),
                    'exchange': kwargs.get('exchange', 'SSE' if market_type == 'STOCK' else 'CFFEX'),
                    'listing_date': kwargs.get('listing_date'),
                    'is_active': kwargs.get('is_active', True),
                    'metadata': kwargs.get('metadata', {}),
                }
            )
            logger.info(f"{'创建' if created else '更新'}标的: {instrument}")
            return instrument
        except Exception as e:
            logger.error(f"导入标的 {symbol} 失败: {e}")
            raise

    @transaction.atomic
    def import_kline_data(self, instrument_id, start_date, end_date, period='1d'):
        """导入K线数据"""
        try:
            instrument = Instrument.objects.get(id=instrument_id)

            # 获取数据
            if instrument.market_type == 'STOCK':
                data = self.fetcher.fetch_stock_daily(instrument.symbol, start_date, end_date)
            else:
                data = self.fetcher.fetch_futures_daily(instrument.symbol, start_date, end_date)

            if not data:
                logger.warning(f"未获取到 {instrument.symbol} 的数据")
                return 0

            # 删除已存在的数据
            KLine.objects.filter(
                instrument=instrument,
                period=period,
                trade_date__gte=start_date,
                trade_date__lte=end_date
            ).delete()

            # 批量创建
            klines = [
                KLine(
                    instrument=instrument,
                    period=period,
                    **item
                ) for item in data
            ]
            KLine.objects.bulk_create(klines, batch_size=1000)

            logger.info(f"导入 {instrument.symbol} K线数据 {len(klines)} 条")
            return len(klines)
        except Instrument.DoesNotExist:
            logger.error(f"标的 ID {instrument_id} 不存在")
            raise
        except Exception as e:
            logger.error(f"导入K线数据失败: {e}")
            raise

    def update_latest_data(self, instrument_id, days=30):
        """更新最新数据"""
        try:
            instrument = Instrument.objects.get(id=instrument_id)

            # 获取最后一条数据的日期
            last_kline = KLine.objects.filter(
                instrument=instrument,
                period='1d'
            ).order_by('-trade_date').first()

            if last_kline:
                start_date = (last_kline.trade_date + timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            end_date = datetime.now().strftime('%Y-%m-%d')

            # 如果开始日期大于结束日期，说明数据已是最新
            if start_date > end_date:
                logger.info(f"{instrument.symbol} 数据已是最新，无需更新")
                return 0

            return self.import_kline_data(instrument_id, start_date, end_date)
        except Exception as e:
            logger.error(f"更新最新数据失败: {e}")
            raise
