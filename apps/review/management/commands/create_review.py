from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from apps.market_data.models import Instrument
from apps.review.services import ReviewService


class Command(BaseCommand):
    help = '创建复盘记录'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbol',
            type=str,
            required=True,
            help='标的代码'
        )
        parser.add_argument(
            '--date',
            type=str,
            help='交易日期 (YYYY-MM-DD)，默认为今天'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['DAILY', 'WEEKLY', 'MONTHLY'],
            default='DAILY',
            help='复盘类型'
        )

    def handle(self, *args, **options):
        symbol = options['symbol']
        review_type = options['type']

        # 解析日期
        if options['date']:
            try:
                trade_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR('日期格式错误，请使用 YYYY-MM-DD 格式'))
                return
        else:
            trade_date = timezone.now().date()

        # 查找标的
        try:
            instrument = Instrument.objects.get(symbol=symbol)
        except Instrument.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'标的 {symbol} 不存在'))
            return

        # 创建复盘记录
        try:
            review = ReviewService.create_review_with_analysis(
                instrument_id=instrument.id,
                trade_date=trade_date,
                review_type=review_type
            )

            self.stdout.write(self.style.SUCCESS(
                f'成功创建复盘记录: {review.instrument.symbol} {review.trade_date} {review.get_review_type_display()}'
            ))
            self.stdout.write(f'市场阶段: {review.get_market_phase_display()}')
            self.stdout.write(f'支撑位: {review.key_levels.get("support", [])}')
            self.stdout.write(f'阻力位: {review.key_levels.get("resistance", [])}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'创建复盘记录失败: {str(e)}'))
