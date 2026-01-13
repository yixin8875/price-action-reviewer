import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { KLine } from '../../types';

interface KLineChartProps {
  data: KLine[];
  indicators?: Record<string, any>;
}

export default function KLineChart({ data, indicators = {} }: KLineChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || data.length === 0) return;

    const chart = echarts.init(chartRef.current);

    const chartData = data.map((item) => [
      item.trade_date,
      parseFloat(item.open_price),
      parseFloat(item.close_price),
      parseFloat(item.low_price),
      parseFloat(item.high_price),
      parseFloat(item.volume),
    ]);

    const series: any[] = [
      {
        name: 'K线',
        type: 'candlestick',
        data: chartData.map((item) => item.slice(1, 5)),
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a',
        },
        xAxisIndex: 0,
        yAxisIndex: 0,
      },
    ];

    // Add MA indicators to main chart
    const maColors: Record<string, string> = {
      MA5: '#FF9800',
      MA10: '#2196F3',
      MA20: '#9C27B0',
    };

    Object.keys(indicators).forEach((key) => {
      if (key.startsWith('MA') && indicators[key]?.length > 0) {
        series.push({
          name: key,
          type: 'line',
          data: indicators[key].map((item: any) => item.value),
          smooth: true,
          lineStyle: { width: 2, color: maColors[key] },
          xAxisIndex: 0,
          yAxisIndex: 0,
        });
      }
    });

    // Add volume bar
    series.push({
      name: '成交量',
      type: 'bar',
      data: chartData.map((item) => item[5]),
      xAxisIndex: 1,
      yAxisIndex: 1,
    });

    // Add sub-chart indicators (MACD, RSI, KDJ)
    let gridIndex = 2;
    const grids: any[] = [
      { left: '10%', right: '10%', height: '50%' },
      { left: '10%', right: '10%', top: '65%', height: '10%' },
    ];
    const xAxis: any[] = [
      { type: 'category', data: chartData.map((item) => item[0]), gridIndex: 0 },
      { type: 'category', data: chartData.map((item) => item[0]), gridIndex: 1 },
    ];
    const yAxis: any[] = [
      { scale: true, gridIndex: 0 },
      { scale: true, gridIndex: 1 },
    ];

    if (indicators.RSI?.length > 0) {
      grids.push({ left: '10%', right: '10%', top: '78%', height: '10%' });
      xAxis.push({ type: 'category', data: chartData.map((item) => item[0]), gridIndex });
      yAxis.push({ scale: true, gridIndex });
      series.push({
        name: 'RSI',
        type: 'line',
        data: indicators.RSI.map((item: any) => item.value),
        lineStyle: { color: '#FFC107' },
        xAxisIndex: gridIndex,
        yAxisIndex: gridIndex,
      });
      gridIndex++;
    }

    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
      },
      legend: {
        data: series.map((s) => s.name),
        top: 0,
      },
      grid: grids,
      xAxis,
      yAxis,
      series,
    };

    chart.setOption(option);

    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.dispose();
    };
  }, [data, indicators]);

  return <div ref={chartRef} style={{ width: '100%', height: '600px' }} />;
}
