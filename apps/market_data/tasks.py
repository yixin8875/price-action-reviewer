from celery import shared_task
from datetime import datetime, timedelta
import logging
from .models import Instrument
from .services import MarketDataService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_daily_data(self):
    """同步每日数据（定时任务）"""
    logger.info("开始同步每日数据")
    service = MarketDataService()

    instruments = Instrument.objects.filter(is_active=True)
    success_count = 0
    fail_count = 0

    for instrument in instruments:
        try:
            count = service.update_latest_data(instrument.id, days=1)
            logger.info(f"同步 {instrument.symbol} 成功，更新 {count} 条数据")
            success_count += 1

            # 触发技术指标计算
            from apps.technical_analysis.tasks import calculate_indicators_task
            calculate_indicators_task.delay(instrument.id)

        except Exception as e:
            logger.error(f"同步 {instrument.symbol} 失败: {e}")
            fail_count += 1

    logger.info(f"每日数据同步完成，成功: {success_count}, 失败: {fail_count}")
    return {'success': success_count, 'fail': fail_count}


@shared_task(bind=True, max_retries=3)
def sync_instrument_data(self, instrument_id, days=1):
    """同步单个标的数据"""
    try:
        service = MarketDataService()
        count = service.update_latest_data(instrument_id, days=days)
        logger.info(f"同步标的 {instrument_id} 成功，更新 {count} 条数据")
        return {'instrument_id': instrument_id, 'count': count}
    except Exception as e:
        logger.error(f"同步标的 {instrument_id} 失败: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def import_historical_data(self, symbol, start_date, end_date):
    """导入历史数据"""
    try:
        service = MarketDataService()
        instrument = Instrument.objects.get(symbol=symbol)

        # 分批次导入，每次30天
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        total_count = 0

        while start < end:
            batch_end = min(start + timedelta(days=30), end)
            count = service.import_kline_data(
                instrument.id,
                start.strftime('%Y-%m-%d'),
                batch_end.strftime('%Y-%m-%d')
            )
            total_count += count
            logger.info(f"导入 {symbol} {start.date()} 到 {batch_end.date()} 数据 {count} 条")
            start = batch_end + timedelta(days=1)

        logger.info(f"导入 {symbol} 历史数据完成，共 {total_count} 条")
        return {'symbol': symbol, 'count': total_count}
    except Exception as e:
        logger.error(f"导入 {symbol} 历史数据失败: {e}")
        raise self.retry(exc=e, countdown=300)
