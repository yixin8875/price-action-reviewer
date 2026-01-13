from django.core.management.base import BaseCommand, CommandError
from apps.market_data.models import Instrument
from apps.technical_analysis.services import TechnicalAnalysisService


class Command(BaseCommand):
    help = '计算技术指标'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbol',
            type=str,
            help='标的代码（如：000001.SZ）'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='计算所有活跃标的'
        )
        parser.add_argument(
            '--period',
            type=str,
            default='1d',
            help='K线周期（默认：1d）'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='限制计算最近N条数据'
        )
        parser.add_argument(
            '--with-patterns',
            action='store_true',
            help='同时识别形态'
        )
        parser.add_argument(
            '--with-sr',
            action='store_true',
            help='同时更新支撑阻力位'
        )

    def handle(self, *args, **options):
        symbol = options.get('symbol')
        all_instruments = options.get('all')
        period = options.get('period')
        limit = options.get('limit')
        with_patterns = options.get('with_patterns')
        with_sr = options.get('with_sr')

        if not symbol and not all_instruments:
            raise CommandError('请指定 --symbol 或 --all')

        if symbol and all_instruments:
            raise CommandError('--symbol 和 --all 不能同时使用')

        # 获取要处理的标的
        if symbol:
            try:
                instruments = [Instrument.objects.get(symbol=symbol)]
            except Instrument.DoesNotExist:
                raise CommandError(f'标的 {symbol} 不存在')
        else:
            instruments = Instrument.objects.filter(is_active=True)

        total_instruments = len(instruments)
        self.stdout.write(f'开始处理 {total_instruments} 个标的...')

        success_count = 0
        error_count = 0

        for i, instrument in enumerate(instruments, 1):
            try:
                self.stdout.write(f'[{i}/{total_instruments}] 处理 {instrument.symbol} - {instrument.name}')

                # 计算技术指标
                indicator_count = TechnicalAnalysisService.calculate_and_save_indicators(
                    instrument.id,
                    period=period,
                    limit=limit
                )
                self.stdout.write(self.style.SUCCESS(f'  ✓ 计算了 {indicator_count} 个指标'))

                # 识别形态
                if with_patterns:
                    pattern_count = TechnicalAnalysisService.detect_and_save_patterns(
                        instrument.id,
                        period=period
                    )
                    self.stdout.write(self.style.SUCCESS(f'  ✓ 识别了 {pattern_count} 个形态'))

                # 更新支撑阻力位
                if with_sr:
                    sr_count = TechnicalAnalysisService.update_support_resistance(
                        instrument.id,
                        period=period
                    )
                    self.stdout.write(self.style.SUCCESS(f'  ✓ 更新了 {sr_count} 个支撑阻力位'))

                success_count += 1

            except ValueError as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ 跳过: {str(e)}'))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ 错误: {str(e)}'))
                error_count += 1

        # 输出统计
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'处理完成！'))
        self.stdout.write(f'成功: {success_count}')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'失败/跳过: {error_count}'))
