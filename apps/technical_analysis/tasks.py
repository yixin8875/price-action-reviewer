from celery import shared_task
import logging
from apps.market_data.models import Instrument
from .services import TechnicalAnalysisService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def calculate_indicators_task(self, instrument_id, period='1d'):
    """计算技术指标"""
    try:
        instrument = Instrument.objects.get(id=instrument_id)
        count = TechnicalAnalysisService.calculate_and_save_indicators(
            instrument_id, period
        )
        logger.info(f"计算 {instrument.symbol} 技术指标成功，共 {count} 个指标")
        return {'instrument_id': instrument_id, 'count': count}
    except Exception as e:
        logger.error(f"计算标的 {instrument_id} 技术指标失败: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def detect_patterns_task(self, instrument_id):
    """识别形态"""
    try:
        instrument = Instrument.objects.get(id=instrument_id)
        count = TechnicalAnalysisService.detect_and_save_patterns(instrument_id)
        logger.info(f"识别 {instrument.symbol} 形态成功，共 {count} 个形态")
        return {'instrument_id': instrument_id, 'count': count}
    except Exception as e:
        logger.error(f"识别标的 {instrument_id} 形态失败: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True)
def batch_calculate_indicators(self):
    """批量计算指标（定时任务）"""
    logger.info("开始批量计算技术指标")
    instruments = Instrument.objects.filter(is_active=True)
    success_count = 0
    fail_count = 0

    for instrument in instruments:
        try:
            count = TechnicalAnalysisService.calculate_and_save_indicators(
                instrument.id, period='1d'
            )
            logger.info(f"计算 {instrument.symbol} 技术指标成功，共 {count} 个指标")
            success_count += 1
        except Exception as e:
            logger.error(f"计算 {instrument.symbol} 技术指标失败: {e}")
            fail_count += 1

    logger.info(f"批量计算技术指标完成，成功: {success_count}, 失败: {fail_count}")
    return {'success': success_count, 'fail': fail_count}


@shared_task(bind=True)
def batch_detect_patterns(self):
    """批量识别形态（定时任务）"""
    logger.info("开始批量识别形态")
    instruments = Instrument.objects.filter(is_active=True)
    success_count = 0
    fail_count = 0

    for instrument in instruments:
        try:
            count = TechnicalAnalysisService.detect_and_save_patterns(instrument.id)
            logger.info(f"识别 {instrument.symbol} 形态成功，共 {count} 个形态")
            success_count += 1
        except Exception as e:
            logger.error(f"识别 {instrument.symbol} 形态失败: {e}")
            fail_count += 1

    logger.info(f"批量识别形态完成，成功: {success_count}, 失败: {fail_count}")
    return {'success': success_count, 'fail': fail_count}
