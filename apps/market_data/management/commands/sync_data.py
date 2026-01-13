from django.core.management.base import BaseCommand
from apps.market_data.services import MarketDataService
from apps.market_data.data_fetcher import AkshareDataFetcher
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '同步市场数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['stock', 'futures', 'all'],
            default='all',
            help='同步类型: stock(股票), futures(期货), all(全部)'
        )
        parser.add_argument(
            '--symbol',
            type=str,
            help='指定标的代码'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='同步最近N天的数据'
        )
        parser.add_argument(
            '--sync-list',
            action='store_true',
            help='同步标的列表'
        )

    def handle(self, *args, **options):
        service = MarketDataService()
        fetcher = AkshareDataFetcher()

        sync_type = options['type']
        symbol = options['symbol']
        days = options['days']
        sync_list = options['sync_list']

        # 同步标的列表
        if sync_list:
            if sync_type in ['stock', 'all']:
                self.stdout.write('同步股票列表...')
                stocks = fetcher.fetch_stock_list()
                for stock in stocks[:100]:  # 限制数量避免过长
                    try:
                        service.import_instrument(
                            symbol=stock['symbol'],
                            market_type='STOCK',
                            name=stock['name'],
                            exchange='SSE' if stock['symbol'].startswith('6') else 'SZSE'
                        )
                    except Exception as e:
                        logger.error(f"导入股票 {stock['symbol']} 失败: {e}")
                self.stdout.write(self.style.SUCCESS(f'股票列表同步完成'))

            if sync_type in ['futures', 'all']:
                self.stdout.write('同步期货列表...')
                futures = fetcher.fetch_futures_list()
                for future in futures:
                    try:
                        service.import_instrument(
                            symbol=future['symbol'],
                            market_type='FUTURES',
                            name=future['name'],
                            exchange='CFFEX'
                        )
                    except Exception as e:
                        logger.error(f"导入期货 {future['symbol']} 失败: {e}")
                self.stdout.write(self.style.SUCCESS(f'期货列表同步完成'))

        # 同步K线数据
        if symbol:
            from apps.market_data.models import Instrument
            try:
                instrument = Instrument.objects.get(symbol=symbol)
                self.stdout.write(f'同步 {symbol} 最近 {days} 天数据...')

                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

                count = service.import_kline_data(instrument.id, start_date, end_date)
                self.stdout.write(self.style.SUCCESS(f'同步完成，共 {count} 条数据'))
            except Instrument.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'标的 {symbol} 不存在'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'同步失败: {e}'))
