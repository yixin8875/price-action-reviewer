# Django Admin 图表定制功能实现说明

## 实现概述

已成功实现 Django Admin 的图表定制功能，集成 ECharts 展示 K线图和技术指标。

## 已创建的文件

### 1. 核心工具模块
**文件路径**: `/Users/boohee/Documents/trae_projects/price-action-reviewer/apps/core/chart_utils.py`

- `ChartDataBuilder` 类：构建 ECharts K线图配置
- `build_kline_option()` 方法：生成 JSON 格式的图表配置
- 支持 K线主图、成交量副图、技术指标叠加
- 红涨绿跌配色（中国风格）
- 支持数据缩放和交互

### 2. Instrument Admin 扩展
**文件路径**: `/Users/boohee/Documents/trae_projects/price-action-reviewer/apps/market_data/admin.py`

新增功能：
- `view_chart_link()`: 在列表页添加"查看图表"链接
- `get_urls()`: 添加自定义 URL 路由 `/admin/market_data/instrument/<id>/chart/`
- `chart_view()`: 图表视图方法
  - 获取最近100个交易日K线数据
  - 获取 MA5/MA10/MA20 技术指标
  - 使用 `select_related` 优化查询
  - 支持周期切换（日线/周线/月线）

### 3. ReviewRecord Admin 扩展
**文件路径**: `/Users/boohee/Documents/trae_projects/price-action-reviewer/apps/review/admin.py`

新增功能：
- `view_analysis_chart_link()`: 在列表页添加"分析图表"链接
- `analysis_chart_view()`: 复盘分析图表视图
  - 获取复盘日期前后30天的K线数据
  - 查询支撑阻力位数据
  - 在图表上标记关键价位

### 4. 图表模板

#### Instrument K线图模板
**文件路径**: `/Users/boohee/Documents/trae_projects/price-action-reviewer/templates/admin/market_data/kline_chart.html`

功能：
- 继承 `admin/base_site.html` 保持 Admin 风格
- 使用 ECharts CDN（5.4.3版本）
- 周期选择器（日线/周线/月线）
- MA均线开关
- 响应式设计

#### ReviewRecord 分析图表模板
**文件路径**: `/Users/boohee/Documents/trae_projects/price-action-reviewer/templates/admin/review/analysis_chart.html`

功能：
- 显示复盘信息面板
- 显示关键价位列表（支撑位/阻力位）
- 在图表上标记支撑阻力位（虚线）
- 支撑位绿色，阻力位红色

### 5. 静态文件
**文件路径**: `/Users/boohee/Documents/trae_projects/price-action-reviewer/static/admin/css/custom_admin.css`

- 图表容器样式
- 控制面板样式
- 响应式布局（移动端适配）

## 使用方法

### 查看 Instrument K线图
1. 进入 Django Admin: `/admin/market_data/instrument/`
2. 点击任意品种行的"查看图表"链接
3. 在图表页面可以：
   - 切换周期（日线/周线/月线）
   - 开关 MA 均线显示
   - 使用鼠标滚轮缩放
   - 拖动数据缩放条查看不同时间段

### 查看 ReviewRecord 分析图表
1. 进入 Django Admin: `/admin/review/reviewrecord/`
2. 点击任意复盘记录的"分析图表"链接
3. 查看：
   - 复盘日期前后30天的K线走势
   - 关键价位信息面板
   - 图表上的支撑阻力位标记线

## 技术特点

### ECharts 配置
- 使用 candlestick 类型展示K线
- 红涨绿跌（color: '#ef232a', color0: '#14b143'）
- 成交量柱状图根据涨跌着色
- 双网格布局（主图+副图）
- dataZoom 支持缩放和拖动

### 数据优化
- 使用 `select_related()` 减少数据库查询
- K线数据限制在100-200个数据点
- 技术指标数据按需加载

### 安全性
- 使用 `admin_site.admin_view()` 装饰器保护视图
- 使用 `format_html()` 安全输出 HTML
- 图表配置使用 `|safe` 过滤器

## 数据格式

### K线数据格式
```python
[
    {
        'trade_date': '2024-01-01',
        'open_price': 10.0,
        'high_price': 10.5,
        'low_price': 9.8,
        'close_price': 10.2,
        'volume': 1000000
    },
    ...
]
```

### 技术指标数据格式
```python
{
    'MA5': [10.1, 10.2, 10.3, ...],
    'MA10': [10.0, 10.1, 10.2, ...],
    'MA20': [9.9, 10.0, 10.1, ...]
}
```

## 注意事项

1. ECharts 使用 CDN，需要网络连接
2. 图表容器需要明确高度（600px）才能正常显示
3. 技术指标数据需要先通过 `calculate_indicators` 命令计算
4. 支撑阻力位需要先在数据库中创建记录

## 扩展建议

1. 添加更多技术指标（MACD、RSI、KDJ）
2. 支持更多周期（分钟线、小时线）
3. 添加图表导出功能（PNG/PDF）
4. 实现实时数据更新（WebSocket）
5. 添加多品种对比图表
