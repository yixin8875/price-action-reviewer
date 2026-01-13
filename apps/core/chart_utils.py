import json
from decimal import Decimal


class ChartDataBuilder:
    """ECharts K线图配置构建器"""

    @staticmethod
    def build_kline_option(kline_data, indicators=None):
        """
        构建K线图 ECharts 配置

        Args:
            kline_data: K线数据列表 [{'trade_date': '2024-01-01', 'open_price': 10.0, ...}, ...]
            indicators: 技术指标数据 {'MA5': [10.1, ...], 'MA10': [...], ...}

        Returns:
            JSON格式的 ECharts option 配置
        """
        if not kline_data:
            return json.dumps({})

        # 提取数据
        dates = [str(item['trade_date']) for item in kline_data]
        kline_values = [
            [
                float(item['open_price']),
                float(item['close_price']),
                float(item['low_price']),
                float(item['high_price'])
            ]
            for item in kline_data
        ]
        volumes = [float(item['volume']) for item in kline_data]

        # 成交量颜色（根据涨跌）
        volume_colors = [
            '#ef232a' if kline_values[i][1] >= kline_values[i][0] else '#14b143'
            for i in range(len(kline_values))
        ]

        # 构建series
        series = [
            {
                'name': 'K线',
                'type': 'candlestick',
                'data': kline_values,
                'itemStyle': {
                    'color': '#ef232a',  # 涨红
                    'color0': '#14b143',  # 跌绿
                    'borderColor': '#ef232a',
                    'borderColor0': '#14b143'
                }
            },
            {
                'name': '成交量',
                'type': 'bar',
                'xAxisIndex': 1,
                'yAxisIndex': 1,
                'data': [
                    {
                        'value': volumes[i],
                        'itemStyle': {'color': volume_colors[i]}
                    }
                    for i in range(len(volumes))
                ]
            }
        ]

        # 添加技术指标
        legend_data = ['K线', '成交量']
        if indicators:
            for name, values in indicators.items():
                if values:
                    series.append({
                        'name': name,
                        'type': 'line',
                        'data': values,
                        'smooth': True,
                        'lineStyle': {'width': 1}
                    })
                    legend_data.append(name)

        # 构建完整配置
        option = {
            'title': {'text': 'K线图', 'left': 'center'},
            'legend': {
                'data': legend_data,
                'top': 30
            },
            'tooltip': {
                'trigger': 'axis',
                'axisPointer': {'type': 'cross'}
            },
            'grid': [
                {'left': '10%', 'right': '10%', 'top': '15%', 'height': '50%'},
                {'left': '10%', 'right': '10%', 'top': '70%', 'height': '15%'}
            ],
            'xAxis': [
                {
                    'type': 'category',
                    'data': dates,
                    'gridIndex': 0,
                    'axisLabel': {'show': False}
                },
                {
                    'type': 'category',
                    'data': dates,
                    'gridIndex': 1
                }
            ],
            'yAxis': [
                {'scale': True, 'gridIndex': 0, 'splitLine': {'show': True}},
                {'scale': True, 'gridIndex': 1, 'splitLine': {'show': False}}
            ],
            'dataZoom': [
                {'type': 'inside', 'xAxisIndex': [0, 1], 'start': 0, 'end': 100},
                {'show': True, 'xAxisIndex': [0, 1], 'type': 'slider', 'bottom': '5%', 'start': 0, 'end': 100}
            ],
            'series': series
        }

        return json.dumps(option, ensure_ascii=False)
