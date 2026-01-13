# Technical Analysis Module

技术分析模块，提供技术指标计算、形态识别和支撑阻力位检测功能。

## 功能特性

### 1. 技术指标计算
- **MA (移动平均线)**: 5, 10, 20, 60 日均线
- **EMA (指数移动平均)**: 12, 26 日指数均线
- **MACD**: 快线、慢线、柱状图
- **RSI**: 相对强弱指标
- **KDJ**: 随机指标
- **BOLL (布林带)**: 上轨、中轨、下轨

### 2. 形态识别
- 趋势判断（上升/下降/盘整）
- 双顶/双底形态
- 头肩顶/头肩底形态

### 3. 支撑阻力位
- 自动识别支撑位和阻力位
- 价格聚类分析
- 强度评级（1-5级）

## 数据模型

### Indicator（技术指标）
存储每个K线的技术指标数据。

### Pattern（形态）
存储识别出的价格形态。

### SupportResistance（支撑阻力位）
存储支撑位和阻力位信息。

## 使用方法

### 命令行工具

```bash
# 计算单个标的的技术指标
python manage.py calculate_indicators --symbol 000001.SZ

# 计算所有活跃标的
python manage.py calculate_indicators --all

# 同时识别形态和支撑阻力位
python manage.py calculate_indicators --symbol 000001.SZ --with-patterns --with-sr

# 指定K线周期
python manage.py calculate_indicators --symbol 000001.SZ --period 1d

# 限制计算最近N条数据
python manage.py calculate_indicators --symbol 000001.SZ --limit 100
```

### 编程接口

```python
from apps.technical_analysis.services import TechnicalAnalysisService

# 计算技术指标
indicator_count = TechnicalAnalysisService.calculate_and_save_indicators(
    instrument_id=1,
    period='1d'
)

# 识别形态
pattern_count = TechnicalAnalysisService.detect_and_save_patterns(
    instrument_id=1,
    period='1d',
    lookback_days=120
)

# 更新支撑阻力位
sr_count = TechnicalAnalysisService.update_support_resistance(
    instrument_id=1,
    period='1d',
    lookback_days=120
)
```

## 依赖项

```
pandas
numpy
scipy
scikit-learn
```

安装依赖：
```bash
pip install -r requirements.txt
```

## 注意事项

1. 计算指标前需要确保有足够的K线数据（至少60个数据点）
2. 批量计算时会自动跳过数据不足的标的
3. 指标数据以JSON格式存储，便于灵活扩展
4. 支撑阻力位会定期更新，旧的位会被标记为无效

## 算法说明

### 技术指标
使用 pandas 实现基础技术指标计算，为后续集成 TA-Lib 预留接口。

### 形态识别
- **支撑阻力位**: 使用局部极值法和DBSCAN聚类算法
- **趋势判断**: 基于移动平均线斜率和价格位置关系
- **双顶双底**: 基于峰值检测和价格相似度
- **头肩形态**: 基于三个峰值的高度关系

## 未来扩展

- 集成 TA-Lib 库提供更多技术指标
- 增加更多经典形态识别（三角形、旗形等）
- 实现形态突破信号检测
- 添加技术指标组合策略
