# 价格行为复盘专家系统

基于 Django 的股票和期货价格行为复盘分析系统，支持数据采集、技术分析、形态识别和交易复盘。

## 系统特性

### 核心功能
- **市场数据管理**: 对接 akshare 获取股票和期货数据
- **技术指标计算**: MA、EMA、MACD、RSI、KDJ、布林带等
- **形态识别**: 支撑阻力位、趋势判断、双顶双底、头肩形态
- **复盘记录**: 交易日志、分析笔记、评分系统
- **可视化图表**: 集成 ECharts 展示交互式 K线图
- **异步任务**: Celery 定时同步数据和计算指标

### 技术栈
- **后端**: Django 5.0+
- **数据库**: SQLite（可切换 PostgreSQL）
- **数据源**: akshare
- **任务队列**: Celery + Redis
- **图表**: ECharts 5.4
- **数据分析**: pandas, numpy, scipy, scikit-learn

## 快速开始

### 1. 环境准备

```bash
# 克隆项目（如果从 Git）
cd /Users/boohee/Documents/trae_projects/price-action-reviewer

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件（可选，使用默认配置即可）
```

### 3. 初始化数据库

```bash
# 运行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 4. 启动开发服务器

```bash
# 启动 Django 开发服务器
python manage.py runserver

# 访问 http://127.0.0.1:8000/admin/
```

### 5. 同步市场数据

```bash
# 同步股票列表（前100只）
python manage.py sync_data --sync-list --type stock

# 同步指定股票的历史数据
python manage.py sync_data --symbol 600000 --days 90

# 同步期货列表
python manage.py sync_data --sync-list --type futures
```

### 6. 计算技术指标

```bash
# 为指定标的计算技术指标
python manage.py calculate_indicators --symbol 600000 --with-patterns --with-sr

# 批量计算所有标的
python manage.py calculate_indicators --all
```

### 7. 启动 Celery（可选）

```bash
# 安装并启动 Redis
brew install redis  # macOS
redis-server

# 启动 Celery worker 和 beat
./scripts/start_celery.sh both

# 或分别启动
./scripts/start_celery.sh worker  # 终端1
./scripts/start_celery.sh beat    # 终端2
```

## 项目结构

```
price-action-reviewer/
├── config/                      # 项目配置
│   ├── settings/               # 分环境配置
│   ├── celery.py              # Celery 配置
│   └── urls.py                # URL 路由
├── apps/                       # 应用模块
│   ├── core/                  # 核心工具
│   │   └── chart_utils.py    # 图表工具
│   ├── market_data/           # 市场数据
│   │   ├── models.py         # Instrument, KLine
│   │   ├── data_fetcher.py   # akshare 数据获取
│   │   ├── services.py       # 业务逻辑
│   │   ├── tasks.py          # Celery 任务
│   │   └── admin.py          # Admin 配置
│   ├── technical_analysis/    # 技术分析
│   │   ├── models.py         # Indicator, Pattern, SupportResistance
│   │   ├── indicators.py     # 指标计算
│   │   ├── pattern_recognition.py  # 形态识别
│   │   ├── services.py       # 业务逻辑
│   │   ├── tasks.py          # Celery 任务
│   │   └── admin.py          # Admin 配置
│   └── review/                # 复盘记录
│       ├── models.py         # ReviewRecord, TradeLog
│       ├── services.py       # 业务逻辑
│       └── admin.py          # Admin 配置
├── templates/                  # 模板文件
│   └── admin/                 # Admin 模板
│       ├── market_data/
│       │   └── kline_chart.html
│       └── review/
│           └── analysis_chart.html
├── static/                     # 静态文件
│   └── admin/
│       └── css/
│           └── custom_admin.css
├── scripts/                    # 脚本
│   └── start_celery.sh        # Celery 启动脚本
├── manage.py                   # Django 管理脚本
├── requirements.txt            # Python 依赖
└── README.md                   # 项目文档
```

## 使用指南

### 数据管理

#### 同步股票数据
```bash
# 同步单只股票
python manage.py sync_data --symbol 600000 --days 30

# 同步多只股票（在 Django shell 中）
python manage.py shell
>>> from apps.market_data.tasks import sync_instrument_data
>>> for i in range(1, 11):
...     sync_instrument_data.delay(instrument_id=i, days=30)
```

#### 同步期货数据
```bash
# 同步期货合约
python manage.py sync_data --symbol IF2401 --days 30
```

### 技术分析

#### 计算技术指标
```bash
# 计算单个标的
python manage.py calculate_indicators --symbol 600000

# 计算并识别形态
python manage.py calculate_indicators --symbol 600000 --with-patterns

# 计算并更新支撑阻力位
python manage.py calculate_indicators --symbol 600000 --with-sr
```

#### 查看技术指标
- 访问 Django Admin: http://127.0.0.1:8000/admin/
- 进入 "Technical Analysis" -> "Indicators"
- 查看计算结果

### 复盘记录

#### 创建复盘记录
```bash
# 使用命令创建
python manage.py create_review --symbol 600000 --date 2024-01-15 --type DAILY

# 或在 Django Admin 中手动创建
```

#### 记录交易日志
- 访问 Django Admin
- 进入 "Review" -> "Trade Logs"
- 添加交易记录（自动计算盈亏）

### 图表查看

#### 查看 K线图
1. 访问 Django Admin
2. 进入 "Market Data" -> "Instruments"
3. 点击任意标的的"查看图表"链接
4. 在图表页面可以：
   - 缩放和拖动查看不同时间段
   - 切换周期（日线/周线/月线）
   - 开关技术指标（MA5/MA10/MA20）

#### 查看复盘分析图
1. 访问 Django Admin
2. 进入 "Review" -> "Review Records"
3. 点击任意记录的"分析图表"链接
4. 查看带支撑阻力位标记的 K线图

## 定时任务

系统配置了以下定时任务（需要启动 Celery）：

| 任务 | 执行时间 | 说明 |
|------|---------|------|
| 同步每日数据 | 工作日 15:30 | 自动同步所有活跃标的的最新数据 |
| 计算技术指标 | 工作日 16:00 | 批量计算所有标的的技术指标 |
| 识别价格形态 | 周日 20:00 | 每周识别价格形态和支撑阻力位 |

## 管理命令

### market_data 模块
```bash
# 同步数据
python manage.py sync_data --help

# 选项：
#   --type {stock,futures,all}  市场类型
#   --symbol SYMBOL             标的代码
#   --days DAYS                 同步天数
#   --sync-list                 同步标的列表
```

### technical_analysis 模块
```bash
# 计算技术指标
python manage.py calculate_indicators --help

# 选项：
#   --symbol SYMBOL    标的代码
#   --all             计算所有标的
#   --period PERIOD   K线周期
#   --limit LIMIT     限制数据量
#   --with-patterns   同时识别形态
#   --with-sr         同时更新支撑阻力位
```

### review 模块
```bash
# 创建复盘记录
python manage.py create_review --help

# 选项：
#   --symbol SYMBOL   标的代码（必需）
#   --date DATE       交易日期（YYYY-MM-DD）
#   --type TYPE       复盘类型（DAILY/WEEKLY/MONTHLY）
```

## 数据模型

### Instrument（市场标的）
- 股票和期货的基础信息
- 代码、名称、市场类型、交易所等

### KLine（K线数据）
- OHLC 价格数据
- 成交量、成交额
- 持仓量（期货）

### Indicator（技术指标）
- MA、EMA、MACD、RSI、KDJ、BOLL
- JSON 格式存储指标数据

### Pattern（形态识别）
- 头肩顶底、双顶双底
- 趋势判断
- 置信度评分

### SupportResistance（支撑阻力位）
- 支撑位和阻力位
- 强度评级（1-5）
- 触及次数跟踪

### ReviewRecord（复盘记录）
- 日/周/月复盘
- 市场阶段判断
- 关键价位记录
- 分析笔记和评分

### TradeLog（交易日志）
- 做多/做空记录
- 入场/出场价格
- 自动计算盈亏
- 交易理由和经验教训

## 常见问题

### 1. akshare 数据获取失败
- 检查网络连接
- akshare 接口可能有调用频率限制，系统已内置延迟
- 部分接口可能需要更新 akshare 版本

### 2. Celery 任务不执行
- 确保 Redis 已启动：`redis-cli ping`
- 检查 Celery worker 是否运行
- 检查 Celery beat 是否运行
- 查看日志：`celery -A config worker -l debug`

### 3. 图表不显示
- 检查浏览器控制台是否有 JavaScript 错误
- 确保 ECharts CDN 可访问
- 检查是否有 K线数据

### 4. 技术指标计算失败
- 确保有足够的 K线数据（至少60个数据点）
- 检查数据质量（是否有缺失值）
- 查看日志获取详细错误信息

## 开发计划

### 已完成
- ✅ Django 项目基础结构
- ✅ 市场数据采集（akshare 集成）
- ✅ 技术指标计算（6种常用指标）
- ✅ 形态识别（支撑阻力位、趋势、双顶双底、头肩形态）
- ✅ 复盘记录管理
- ✅ Django Admin 定制
- ✅ ECharts 图表集成
- ✅ Celery 异步任务
- ✅ 定时任务调度

### 待扩展（可选）
- [ ] 更多技术指标（ATR、OBV、威廉指标等）
- [ ] 更复杂的形态识别（三角形、旗形、楔形等）
- [ ] 回测系统
- [ ] 策略信号生成
- [ ] 数据导出功能（Excel、CSV）
- [ ] 移动端适配
- [ ] 多用户支持
- [ ] 实时数据推送

## 技术文档

- [Celery 使用指南](CELERY_USAGE.md)
- [图表实现说明](CHART_IMPLEMENTATION.md)
- [技术分析模块文档](apps/technical_analysis/README.md)

## 许可证

本项目仅供个人学习和研究使用。

## 联系方式

如有问题或建议，请提交 Issue。
