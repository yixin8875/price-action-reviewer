# Price Action Reviewer API 文档

## 概述

价格行为复盘系统的 RESTful API，提供完整的市场数据、技术分析和复盘记录管理功能。

## 技术栈

- Django 4.2+
- Django REST Framework 3.14+
- JWT 认证 (djangorestframework-simplejwt)
- API 文档 (drf-spectacular)
- CORS 支持 (django-cors-headers)
- 过滤和搜索 (django-filter)

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1/`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **分页**: 默认 20 条/页，最大 100 条/页

## 认证

### 获取 Token

```bash
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "testuser",
  "password": "testpass123"
}
```

响应:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 刷新 Token

```bash
POST /api/v1/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 验证 Token

```bash
POST /api/v1/auth/verify/
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 使用 Token

在所有 API 请求中添加 Authorization header:

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## API 端点

### 1. 交易品种 (Instruments)

#### 列表查询
```bash
GET /api/v1/instruments/
GET /api/v1/instruments/?market_type=STOCK
GET /api/v1/instruments/?exchange=SZSE
GET /api/v1/instruments/?is_active=true
GET /api/v1/instruments/?search=平安
```

#### 创建
```bash
POST /api/v1/instruments/
Content-Type: application/json

{
  "symbol": "000001",
  "name": "平安银行",
  "market_type": "STOCK",
  "exchange": "SZSE",
  "is_active": true
}
```

#### 详情
```bash
GET /api/v1/instruments/{id}/
```

#### 更新
```bash
PUT /api/v1/instruments/{id}/
PATCH /api/v1/instruments/{id}/
```

#### 删除
```bash
DELETE /api/v1/instruments/{id}/
```

### 2. K线数据 (KLines)

#### 列表查询
```bash
GET /api/v1/klines/
GET /api/v1/klines/?instrument={id}
GET /api/v1/klines/?period=1d
GET /api/v1/klines/?trade_date=2024-01-13
GET /api/v1/klines/?search=000001
```

#### 创建
```bash
POST /api/v1/klines/
Content-Type: application/json

{
  "instrument": 1,
  "period": "1d",
  "trade_date": "2024-01-13",
  "open_price": "10.00",
  "high_price": "10.50",
  "low_price": "9.80",
  "close_price": "10.20",
  "volume": 1000000,
  "amount": "10200000.00"
}
```

### 3. 技术指标 (Indicators)

#### 列表查询
```bash
GET /api/v1/indicators/
GET /api/v1/indicators/?kline={id}
GET /api/v1/indicators/?indicator_type=MA
```

#### 创建
```bash
POST /api/v1/indicators/
Content-Type: application/json

{
  "kline": 1,
  "indicator_type": "MA",
  "indicator_data": {
    "ma5": 10.15,
    "ma10": 10.08,
    "ma20": 10.02
  }
}
```

### 4. 形态识别 (Patterns)

#### 列表查询
```bash
GET /api/v1/patterns/
GET /api/v1/patterns/?instrument={id}
GET /api/v1/patterns/?pattern_type=UPTREND
GET /api/v1/patterns/?start_date=2024-01-01
```

#### 创建
```bash
POST /api/v1/patterns/
Content-Type: application/json

{
  "instrument": 1,
  "pattern_type": "UPTREND",
  "start_date": "2024-01-01",
  "end_date": "2024-01-13",
  "confidence": 85,
  "key_points": {
    "support": [9.80, 9.90],
    "resistance": [10.50, 10.60]
  },
  "description": "明显的上升趋势"
}
```

### 5. 支撑阻力位 (Support/Resistance)

#### 列表查询
```bash
GET /api/v1/support-resistance/
GET /api/v1/support-resistance/?instrument={id}
GET /api/v1/support-resistance/?level_type=SUPPORT
GET /api/v1/support-resistance/?is_active=true
```

#### 创建
```bash
POST /api/v1/support-resistance/
Content-Type: application/json

{
  "instrument": 1,
  "level_type": "SUPPORT",
  "price_level": "9.80",
  "strength": 4,
  "identified_date": "2024-01-13",
  "valid_from": "2024-01-13",
  "touch_count": 3,
  "is_active": true,
  "notes": "强支撑位"
}
```

### 6. 复盘记录 (Reviews)

#### 列表查询
```bash
GET /api/v1/reviews/
GET /api/v1/reviews/?instrument={id}
GET /api/v1/reviews/?review_type=DAILY
GET /api/v1/reviews/?market_phase=UPTREND
GET /api/v1/reviews/?trade_date=2024-01-13
GET /api/v1/reviews/?rating=5
```

#### 创建
```bash
POST /api/v1/reviews/
Content-Type: application/json

{
  "instrument": 1,
  "trade_date": "2024-01-13",
  "review_type": "DAILY",
  "market_phase": "UPTREND",
  "key_levels": {
    "support": [9.80, 9.90],
    "resistance": [10.50, 10.60]
  },
  "analysis_notes": "今日突破关键阻力位",
  "tags": "突破,放量",
  "rating": 4
}
```

### 7. 交易日志 (Trades)

#### 列表查询
```bash
GET /api/v1/trades/
GET /api/v1/trades/?instrument={id}
GET /api/v1/trades/?trade_type=LONG
GET /api/v1/trades/?trade_date=2024-01-13
GET /api/v1/trades/?review_record={id}
```

#### 创建
```bash
POST /api/v1/trades/
Content-Type: application/json

{
  "instrument": 1,
  "trade_date": "2024-01-13",
  "trade_type": "LONG",
  "entry_price": "10.00",
  "exit_price": "10.20",
  "quantity": "1000",
  "stop_loss": "9.80",
  "take_profit": "10.50",
  "entry_reason": "突破关键阻力位",
  "exit_reason": "达到目标价位",
  "lessons_learned": "止盈设置合理"
}
```

## 过滤和搜索

### 过滤参数

所有列表端点支持以下过滤方式:

- **精确匹配**: `?field=value`
- **多值过滤**: `?field=value1&field=value2`
- **日期范围**: `?date_field__gte=2024-01-01&date_field__lte=2024-01-31`

### 搜索参数

使用 `search` 参数进行全文搜索:

```bash
GET /api/v1/instruments/?search=平安
GET /api/v1/reviews/?search=突破
```

### 排序参数

使用 `ordering` 参数进行排序:

```bash
GET /api/v1/klines/?ordering=-trade_date
GET /api/v1/trades/?ordering=profit_loss
```

### 分页参数

```bash
GET /api/v1/instruments/?page=2
GET /api/v1/instruments/?page=1&page_size=50
```

## 响应格式

### 成功响应

列表响应:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/instruments/?page=2",
  "previous": null,
  "results": [...]
}
```

详情响应:
```json
{
  "id": 1,
  "symbol": "000001",
  "name": "平安银行",
  ...
}
```

### 错误响应

```json
{
  "detail": "错误信息"
}
```

或

```json
{
  "field_name": ["错误信息"]
}
```

## HTTP 状态码

- `200 OK` - 请求成功
- `201 Created` - 创建成功
- `204 No Content` - 删除成功
- `400 Bad Request` - 请求参数错误
- `401 Unauthorized` - 未认证
- `403 Forbidden` - 无权限
- `404 Not Found` - 资源不存在
- `500 Internal Server Error` - 服务器错误

## API 文档

访问交互式 API 文档:

- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **OpenAPI Schema**: http://localhost:8000/api/v1/schema/

## 测试账号

- **用户名**: testuser
- **密码**: testpass123

## 启动服务器

```bash
python3 manage.py runserver
```

服务器将在 http://localhost:8000 启动。

## CORS 配置

默认允许以下来源访问 API:

- http://localhost:3000
- http://localhost:8080
- http://127.0.0.1:3000
- http://127.0.0.1:8080

如需添加其他来源，请修改 `config/settings/base.py` 中的 `CORS_ALLOWED_ORIGINS` 配置。

## 示例: 完整工作流

### 1. 登录获取 Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 2. 创建交易品种

```bash
curl -X POST http://localhost:8000/api/v1/instruments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "000001",
    "name": "平安银行",
    "market_type": "STOCK",
    "exchange": "SZSE",
    "is_active": true
  }'
```

### 3. 添加 K线数据

```bash
curl -X POST http://localhost:8000/api/v1/klines/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "instrument": 1,
    "period": "1d",
    "trade_date": "2024-01-13",
    "open_price": "10.00",
    "high_price": "10.50",
    "low_price": "9.80",
    "close_price": "10.20",
    "volume": 1000000
  }'
```

### 4. 创建复盘记录

```bash
curl -X POST http://localhost:8000/api/v1/reviews/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "instrument": 1,
    "trade_date": "2024-01-13",
    "review_type": "DAILY",
    "market_phase": "UPTREND",
    "analysis_notes": "今日突破关键阻力位",
    "rating": 4
  }'
```

### 5. 查询数据

```bash
curl -X GET "http://localhost:8000/api/v1/reviews/?instrument=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
