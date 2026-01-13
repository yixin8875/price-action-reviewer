import akshare as ak
import pandas as pd
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


class AkshareDataFetcher:
    """akshare数据获取器"""

    @staticmethod
    def fetch_stock_daily(symbol, start_date, end_date):
        """获取股票日线数据"""
        try:
            time.sleep(0.5)  # 避免频率限制
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="qfq"  # 前复权
            )
            if df.empty:
                return []

            # 标准化列名
            df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']

            return [{
                'trade_date': datetime.strptime(row['date'], '%Y-%m-%d').date(),
                'open_price': float(row['open']),
                'high_price': float(row['high']),
                'low_price': float(row['low']),
                'close_price': float(row['close']),
                'volume': int(row['volume']),
                'amount': float(row['amount']) if pd.notna(row['amount']) else None,
            } for _, row in df.iterrows()]
        except Exception as e:
            logger.error(f"获取股票 {symbol} 数据失败: {e}")
            return []

    @staticmethod
    def fetch_futures_daily(symbol, start_date, end_date):
        """获取期货日线数据"""
        try:
            time.sleep(0.5)
            df = ak.futures_main_sina(symbol=symbol, start_date=start_date, end_date=end_date)
            if df.empty:
                return []

            return [{
                'trade_date': row['date'].date() if isinstance(row['date'], pd.Timestamp) else datetime.strptime(str(row['date']), '%Y-%m-%d').date(),
                'open_price': float(row['open']),
                'high_price': float(row['high']),
                'low_price': float(row['low']),
                'close_price': float(row['close']),
                'volume': int(row['volume']),
                'open_interest': int(row['hold']) if 'hold' in df.columns and pd.notna(row.get('hold')) else None,
            } for _, row in df.iterrows()]
        except Exception as e:
            logger.error(f"获取期货 {symbol} 数据失败: {e}")
            return []

    @staticmethod
    def fetch_stock_list():
        """获取股票列表"""
        try:
            time.sleep(0.5)
            df = ak.stock_info_a_code_name()
            return [{
                'symbol': row['code'],
                'name': row['name'],
            } for _, row in df.iterrows()]
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []

    @staticmethod
    def fetch_futures_list():
        """获取期货合约列表"""
        try:
            time.sleep(0.5)
            df = ak.futures_display_main_sina()
            return [{
                'symbol': row['symbol'],
                'name': row['name'],
            } for _, row in df.iterrows()]
        except Exception as e:
            logger.error(f"获取期货列表失败: {e}")
            return []
