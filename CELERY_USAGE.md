# Celery 异步任务系统使用指南

## 概述

本项目使用 Celery 实现异步任务处理和定时任务调度，主要用于：
- 定时同步市场数据
- 批量计算技术指标
- 识别价格形态
- 更新支撑阻力位

## 系统架构

- **Broker**: Redis（消息队列）
- **Backend**: Redis（结果存储）
- **Scheduler**: Django Celery Beat（定时任务）
- **Worker**: Celery Worker（任务执行）

## 安装依赖

### 1. 安装 Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**验证 Redis 运行:**
```bash
redis-cli ping
# 应返回: PONG
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库迁移

```bash
python manage.py migrate
```

## 启动 Celery

### 方式一：使用启动脚本（推荐）

```bash
# 启动 Worker（执行任务）
./scripts/start_celery.sh worker

# 启动 Beat（定时任务调度）
./scripts/start_celery.sh beat

# 同时启动 Worker 和 Beat（开发环境）
./scripts/start_celery.sh both
```

### 方式二：手动启动

**启动 Worker:**
```bash
celery -A config worker -l info
```

**启动 Beat:**
```bash
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**同时启动（开发环境）:**
```bash
celery -A config worker -B -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## 定时任务配置

系统已配置以下定时任务：

| 任务名称 | 执行时间 | 说明 |
|---------|---------|------|
| sync-daily-data | 工作日 15:30 | 同步每日市场数据 |
| batch-calculate-indicators | 工作日 16:00 | 批量计算技术指标 |
| weekly-pattern-detection | 周日 20:00 | 每周识别价格形态 |

### 修改定时任务

编辑 `config/celery.py` 中的 `beat_schedule` 配置：

```python
app.conf.beat_schedule = {
    'sync-daily-data': {
        'task': 'apps.market_data.tasks.sync_daily_data',
        'schedule': crontab(hour=15, minute=30, day_of_week='1-5'),
    },
}
```

## 手动触发任务

### 在 Python Shell 中

```bash
python manage.py shell
```

```python
# 同步单个标的数据
from apps.market_data.tasks import sync_instrument_data
result = sync_instrument_data.delay(instrument_id=1, days=30)

# 导入历史数据
from apps.market_data.tasks import import_historical_data
result = import_historical_data.delay('000001', '2023-01-01', '2023-12-31')

# 计算技术指标
from apps.technical_analysis.tasks import calculate_indicators_task
result = calculate_indicators_task.delay(instrument_id=1)

# 识别形态
from apps.technical_analysis.tasks import detect_patterns_task
result = detect_patterns_task.delay(instrument_id=1)

# 查看任务状态
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)  # 任务结果
```

### 在 Django Admin 中

访问 `http://localhost:8000/admin/`，可以在以下位置管理定时任务：
- **Periodic tasks**: 查看和管理定时任务
- **Crontab schedules**: 配置 crontab 时间表
- **Task results**: 查看任务执行结果

## 监控任务

### 使用 Flower（推荐）

Flower 是 Celery 的实时监控工具。

**安装:**
```bash
pip install flower
```

**启动:**
```bash
celery -A config flower
# 或使用脚本
./scripts/start_celery.sh flower
```

访问: `http://localhost:5555`

### 查看日志

Worker 和 Beat 的日志会输出到终端，可以重定向到文件：

```bash
celery -A config worker -l info > logs/celery_worker.log 2>&1 &
celery -A config beat -l info > logs/celery_beat.log 2>&1 &
```

## 任务说明

### market_data.tasks

#### sync_daily_data()
- **说明**: 同步所有活跃标的的每日数据
- **触发**: 定时任务（工作日 15:30）
- **手动触发**: `sync_daily_data.delay()`

#### sync_instrument_data(instrument_id, days=1)
- **说明**: 同步单个标的的数据
- **参数**:
  - `instrument_id`: 标的ID
  - `days`: 同步天数（默认1天）
- **手动触发**: `sync_instrument_data.delay(1, days=30)`

#### import_historical_data(symbol, start_date, end_date)
- **说明**: 导入历史数据（分批次）
- **参数**:
  - `symbol`: 标的代码
  - `start_date`: 开始日期（YYYY-MM-DD）
  - `end_date`: 结束日期（YYYY-MM-DD）
- **手动触发**: `import_historical_data.delay('000001', '2023-01-01', '2023-12-31')`

### technical_analysis.tasks

#### calculate_indicators_task(instrument_id, period='1d')
- **说明**: 计算单个标的的技术指标
- **参数**:
  - `instrument_id`: 标的ID
  - `period`: K线周期（默认日线）
- **手动触发**: `calculate_indicators_task.delay(1)`

#### detect_patterns_task(instrument_id)
- **说明**: 识别单个标的的价格形态
- **参数**:
  - `instrument_id`: 标的ID
- **手动触发**: `detect_patterns_task.delay(1)`

#### batch_calculate_indicators()
- **说明**: 批量计算所有活跃标的的技术指标
- **触发**: 定时任务（工作日 16:00）
- **手动触发**: `batch_calculate_indicators.delay()`

#### batch_detect_patterns()
- **说明**: 批量识别所有活跃标的的价格形态
- **触发**: 定时任务（周日 20:00）
- **手动触发**: `batch_detect_patterns.delay()`

## 常见问题

### 1. Redis 连接失败

**错误**: `Error: Redis connection failed`

**解决**:
```bash
# 检查 Redis 是否运行
redis-cli ping

# 启动 Redis
redis-server
# 或
brew services start redis
```

### 2. 任务执行失败

**检查**:
- Worker 是否正常运行
- 数据库连接是否正常
- 任务日志中的错误信息

**重试任务**:
```python
from celery import current_app
current_app.control.revoke(task_id, terminate=True)
```

### 3. 定时任务不执行

**检查**:
- Beat 是否正常运行
- 定时任务配置是否正确
- 时区设置是否正确（Asia/Shanghai）

**查看定时任务**:
```bash
python manage.py shell
```
```python
from django_celery_beat.models import PeriodicTask
for task in PeriodicTask.objects.all():
    print(f"{task.name}: {task.enabled}")
```

### 4. 任务堆积

**清空队列**:
```bash
celery -A config purge
```

**增加 Worker 数量**:
```bash
celery -A config worker -l info --concurrency=4
```

## 生产环境部署

### 使用 Supervisor 管理进程

**安装 Supervisor:**
```bash
pip install supervisor
```

**配置文件** (`/etc/supervisor/conf.d/celery.conf`):
```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A config worker -l info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker_err.log

[program:celery_beat]
command=/path/to/venv/bin/celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat_err.log
```

**启动服务**:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start celery_worker
supervisorctl start celery_beat
```

## 性能优化

### 1. 调整并发数

```bash
# 使用多进程
celery -A config worker -l info --concurrency=4

# 使用 gevent（需要安装 gevent）
celery -A config worker -l info --pool=gevent --concurrency=100
```

### 2. 任务优先级

```python
# 高优先级任务
sync_instrument_data.apply_async(args=[1], priority=9)

# 低优先级任务
batch_calculate_indicators.apply_async(priority=1)
```

### 3. 任务路由

在 `config/celery.py` 中配置：
```python
app.conf.task_routes = {
    'apps.market_data.tasks.*': {'queue': 'data_sync'},
    'apps.technical_analysis.tasks.*': {'queue': 'analysis'},
}
```

启动不同队列的 Worker：
```bash
celery -A config worker -Q data_sync -l info
celery -A config worker -Q analysis -l info
```

## 参考资料

- [Celery 官方文档](https://docs.celeryproject.org/)
- [Django Celery Beat](https://django-celery-beat.readthedocs.io/)
- [Redis 官方文档](https://redis.io/documentation)
