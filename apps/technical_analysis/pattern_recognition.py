import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from sklearn.cluster import DBSCAN


class PatternRecognizer:
    def __init__(self, df):
        """
        初始化形态识别器
        :param df: pandas DataFrame，包含 OHLC 数据
        """
        self.df = df.copy()
        self.df = self.df.sort_index()

    def detect_support_resistance(self, window=20, tolerance=0.02):
        """
        识别支撑阻力位（使用局部极值法）
        :param window: 局部极值窗口大小
        :param tolerance: 价格聚类容差（百分比）
        """
        if len(self.df) < window * 2:
            return []

        # 找局部最高点和最低点
        local_max_idx = argrelextrema(self.df['high'].values, np.greater, order=window)[0]
        local_min_idx = argrelextrema(self.df['low'].values, np.less, order=window)[0]

        resistance_levels = self.df['high'].iloc[local_max_idx].values
        support_levels = self.df['low'].iloc[local_min_idx].values

        # 聚类相近价格
        all_levels = []

        if len(resistance_levels) > 0:
            resistance_clusters = self._cluster_prices(resistance_levels, tolerance)
            all_levels.extend([
                {'type': 'RESISTANCE', 'price': price, 'strength': strength}
                for price, strength in resistance_clusters
            ])

        if len(support_levels) > 0:
            support_clusters = self._cluster_prices(support_levels, tolerance)
            all_levels.extend([
                {'type': 'SUPPORT', 'price': price, 'strength': strength}
                for price, strength in support_clusters
            ])

        return all_levels

    def _cluster_prices(self, prices, tolerance):
        """聚类相近价格"""
        if len(prices) == 0:
            return []

        prices = prices.reshape(-1, 1)
        avg_price = np.mean(prices)
        eps = avg_price * tolerance

        clustering = DBSCAN(eps=eps, min_samples=1).fit(prices)
        labels = clustering.labels_

        clusters = []
        for label in set(labels):
            cluster_prices = prices[labels == label]
            avg = float(np.mean(cluster_prices))
            strength = min(len(cluster_prices), 5)  # 强度1-5
            clusters.append((avg, strength))

        return sorted(clusters, key=lambda x: x[1], reverse=True)

    def detect_trend(self, ma_short=20, ma_long=60):
        """
        判断趋势方向
        :param ma_short: 短期均线周期
        :param ma_long: 长期均线周期
        """
        if len(self.df) < ma_long:
            return None

        ma_short_values = self.df['close'].rolling(window=ma_short).mean()
        ma_long_values = self.df['close'].rolling(window=ma_long).mean()

        current_price = self.df['close'].iloc[-1]
        current_ma_short = ma_short_values.iloc[-1]
        current_ma_long = ma_long_values.iloc[-1]

        # 计算均线斜率
        ma_short_slope = (ma_short_values.iloc[-1] - ma_short_values.iloc[-5]) / 5
        ma_long_slope = (ma_long_values.iloc[-1] - ma_long_values.iloc[-10]) / 10

        if current_ma_short > current_ma_long and ma_short_slope > 0 and ma_long_slope > 0:
            return {
                'type': 'UPTREND',
                'confidence': 80,
                'description': '短期和长期均线均向上，价格在均线之上'
            }
        elif current_ma_short < current_ma_long and ma_short_slope < 0 and ma_long_slope < 0:
            return {
                'type': 'DOWNTREND',
                'confidence': 80,
                'description': '短期和长期均线均向下，价格在均线之下'
            }
        else:
            return {
                'type': 'CONSOLIDATION',
                'confidence': 60,
                'description': '均线交织，趋势不明确'
            }

    def detect_double_top_bottom(self, window=10, tolerance=0.02):
        """
        识别双顶双底（简化版）
        :param window: 峰值检测窗口
        :param tolerance: 价格容差
        """
        if len(self.df) < window * 4:
            return []

        patterns = []

        # 检测双顶
        local_max_idx = argrelextrema(self.df['high'].values, np.greater, order=window)[0]
        if len(local_max_idx) >= 2:
            for i in range(len(local_max_idx) - 1):
                peak1_price = self.df['high'].iloc[local_max_idx[i]]
                peak2_price = self.df['high'].iloc[local_max_idx[i + 1]]

                if abs(peak1_price - peak2_price) / peak1_price < tolerance:
                    patterns.append({
                        'type': 'DOUBLE_TOP',
                        'confidence': 70,
                        'start_idx': local_max_idx[i],
                        'end_idx': local_max_idx[i + 1],
                        'key_points': {
                            'peak1': float(peak1_price),
                            'peak2': float(peak2_price)
                        }
                    })

        # 检测双底
        local_min_idx = argrelextrema(self.df['low'].values, np.less, order=window)[0]
        if len(local_min_idx) >= 2:
            for i in range(len(local_min_idx) - 1):
                bottom1_price = self.df['low'].iloc[local_min_idx[i]]
                bottom2_price = self.df['low'].iloc[local_min_idx[i + 1]]

                if abs(bottom1_price - bottom2_price) / bottom1_price < tolerance:
                    patterns.append({
                        'type': 'DOUBLE_BOTTOM',
                        'confidence': 70,
                        'start_idx': local_min_idx[i],
                        'end_idx': local_min_idx[i + 1],
                        'key_points': {
                            'bottom1': float(bottom1_price),
                            'bottom2': float(bottom2_price)
                        }
                    })

        return patterns

    def detect_head_shoulder(self, window=10, tolerance=0.03):
        """
        识别头肩顶底（简化版）
        :param window: 峰值检测窗口
        :param tolerance: 价格容差
        """
        if len(self.df) < window * 6:
            return []

        patterns = []

        # 检测头肩顶
        local_max_idx = argrelextrema(self.df['high'].values, np.greater, order=window)[0]
        if len(local_max_idx) >= 3:
            for i in range(len(local_max_idx) - 2):
                left_shoulder = self.df['high'].iloc[local_max_idx[i]]
                head = self.df['high'].iloc[local_max_idx[i + 1]]
                right_shoulder = self.df['high'].iloc[local_max_idx[i + 2]]

                # 头部应该高于两肩，两肩高度相近
                if (head > left_shoulder and head > right_shoulder and
                    abs(left_shoulder - right_shoulder) / left_shoulder < tolerance):
                    patterns.append({
                        'type': 'HEAD_SHOULDER',
                        'confidence': 75,
                        'start_idx': local_max_idx[i],
                        'end_idx': local_max_idx[i + 2],
                        'key_points': {
                            'left_shoulder': float(left_shoulder),
                            'head': float(head),
                            'right_shoulder': float(right_shoulder)
                        }
                    })

        # 检测头肩底
        local_min_idx = argrelextrema(self.df['low'].values, np.less, order=window)[0]
        if len(local_min_idx) >= 3:
            for i in range(len(local_min_idx) - 2):
                left_shoulder = self.df['low'].iloc[local_min_idx[i]]
                head = self.df['low'].iloc[local_min_idx[i + 1]]
                right_shoulder = self.df['low'].iloc[local_min_idx[i + 2]]

                # 头部应该低于两肩，两肩高度相近
                if (head < left_shoulder and head < right_shoulder and
                    abs(left_shoulder - right_shoulder) / left_shoulder < tolerance):
                    patterns.append({
                        'type': 'INV_HEAD_SHOULDER',
                        'confidence': 75,
                        'start_idx': local_min_idx[i],
                        'end_idx': local_min_idx[i + 2],
                        'key_points': {
                            'left_shoulder': float(left_shoulder),
                            'head': float(head),
                            'right_shoulder': float(right_shoulder)
                        }
                    })

        return patterns
