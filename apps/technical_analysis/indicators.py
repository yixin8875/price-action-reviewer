import pandas as pd
import numpy as np


class IndicatorCalculator:
    def __init__(self, df):
        """
        初始化指标计算器
        :param df: pandas DataFrame，包含 OHLC 数据（open, high, low, close, volume）
        """
        self.df = df.copy()
        self.df = self.df.sort_index()  # 确保按日期排序

    def calculate_ma(self, periods=[5, 10, 20, 60]):
        """计算移动平均线"""
        result = {}
        for period in periods:
            if len(self.df) >= period:
                result[f'ma{period}'] = float(self.df['close'].rolling(window=period).mean().iloc[-1])
        return result

    def calculate_ema(self, periods=[12, 26]):
        """计算指数移动平均"""
        result = {}
        for period in periods:
            if len(self.df) >= period:
                result[f'ema{period}'] = float(self.df['close'].ewm(span=period, adjust=False).mean().iloc[-1])
        return result

    def calculate_macd(self, fast=12, slow=26, signal=9):
        """计算MACD"""
        if len(self.df) < slow:
            return {}

        ema_fast = self.df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = self.df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            'macd': float(macd_line.iloc[-1]),
            'signal': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }

    def calculate_rsi(self, period=14):
        """计算RSI"""
        if len(self.df) < period + 1:
            return {}

        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return {'rsi': float(rsi.iloc[-1])}

    def calculate_kdj(self, n=9, m1=3, m2=3):
        """计算KDJ"""
        if len(self.df) < n:
            return {}

        low_list = self.df['low'].rolling(window=n).min()
        high_list = self.df['high'].rolling(window=n).max()

        rsv = (self.df['close'] - low_list) / (high_list - low_list) * 100

        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d

        return {
            'k': float(k.iloc[-1]),
            'd': float(d.iloc[-1]),
            'j': float(j.iloc[-1])
        }

    def calculate_bollinger_bands(self, period=20, std=2):
        """计算布林带"""
        if len(self.df) < period:
            return {}

        ma = self.df['close'].rolling(window=period).mean()
        std_dev = self.df['close'].rolling(window=period).std()

        upper = ma + (std_dev * std)
        lower = ma - (std_dev * std)

        return {
            'upper': float(upper.iloc[-1]),
            'middle': float(ma.iloc[-1]),
            'lower': float(lower.iloc[-1])
        }

    def calculate_all(self):
        """计算所有指标"""
        return {
            'ma': self.calculate_ma(),
            'ema': self.calculate_ema(),
            'macd': self.calculate_macd(),
            'rsi': self.calculate_rsi(),
            'kdj': self.calculate_kdj(),
            'boll': self.calculate_bollinger_bands()
        }
