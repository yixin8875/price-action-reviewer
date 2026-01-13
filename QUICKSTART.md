# 快速启动指南

## 后端启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或者单独安装 DRF 相关包:

```bash
pip install djangorestframework djangorestframework-simplejwt django-cors-headers django-filter drf-spectacular
```

### 2. 运行数据库迁移

```bash
python3 manage.py migrate
```

### 3. 创建测试用户和数据

```bash
python3 scripts/setup_api.py
```

这将创建:
- 测试用户: `testuser` / `testpass123`
- 测试交易品种: 000001 (平安银行)
- 测试 K线数据

### 4. 启动开发服务器

```bash
python3 manage.py runserver
```

访问 http://localhost:8000

## 前端启动

### 1. 进入前端目录

```bash
cd /Users/boohee/Documents/trae_projects/price-action-reviewer/frontend
```

### 2. 安装依赖（首次运行）

```bash
npm install
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 4. 登录前端应用

使用后端创建的测试用户登录：
- 用户名: `testuser`
- 密码: `testpass123`

## 项目结构

```
price-action-reviewer/
├── frontend/              # React 前端应用
│   ├── src/
│   │   ├── components/   # 可复用组件
│   │   ├── pages/        # 页面组件
│   │   ├── services/     # API 服务
│   │   ├── stores/       # 状态管理
│   │   ├── theme/        # 主题配置
│   │   └── types/        # TypeScript 类型
│   ├── package.json
│   └── README.md
├── apps/                  # Django 应用
│   ├── market_data/      # 市场数据
│   ├── review/           # 复盘记录
│   └── technical_analysis/ # 技术分析
├── config/                # Django 配置
├── manage.py
└── requirements.txt
```

## 常用命令

### 前端
```bash
npm run dev      # 开发服务器（http://localhost:5173）
npm run build    # 生产构建
npm run preview  # 预览构建
```

### 后端
```bash
python manage.py runserver          # 启动服务器（http://localhost:8000）
python manage.py makemigrations     # 创建迁移
python manage.py migrate            # 应用迁移
python manage.py createsuperuser    # 创建超级用户
```

## API 端点

### 认证
- POST `/api/v1/auth/login/` - 用户登录
- POST `/api/v1/auth/refresh/` - 刷新 Token

### 数据管理
- GET/POST `/api/v1/instruments/` - 交易品种
- GET/POST `/api/v1/klines/` - K线数据
- GET/POST `/api/v1/indicators/` - 技术指标
- GET/POST `/api/v1/patterns/` - 形态识别
- GET/POST `/api/v1/reviews/` - 复盘记录
- GET/POST `/api/v1/trades/` - 交易日志

### API 文档
访问 http://localhost:8000/api/v1/docs/ 查看完整的 Swagger 文档

## 测试 API

### 获取 Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

响应:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 使用 Token 访问 API

```bash
curl -X GET http://localhost:8000/api/v1/instruments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 常见问题

### Q: 如何创建新用户?

```bash
python3 manage.py createsuperuser
```

### Q: 如何重置数据库?

```bash
rm db.sqlite3
python3 manage.py migrate
python3 scripts/setup_api.py
```

### Q: 如何修改 CORS 设置?

编辑 `config/settings/base.py` 中的 `CORS_ALLOWED_ORIGINS`。

### Q: Token 过期了怎么办?

使用 refresh token 获取新的 access token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

### Q: 前端无法连接后端?

1. 确保后端服务运行在 http://localhost:8000
2. 检查 `frontend/.env` 中的 `VITE_API_BASE_URL`
3. 确认后端 CORS 配置允许 http://localhost:5173

### Q: 前端登录失败?

1. 检查后端是否运行
2. 确认用户名和密码正确
3. 查看浏览器控制台网络请求
4. 检查后端日志

## 下一步

1. 使用 Swagger UI 测试所有 API 端点
2. 在前端应用中测试所有功能
3. 添加更多测试数据
4. 开发额外的功能模块
5. 配置生产环境部署

## 相关文档

- [前端实施报告](./FRONTEND_IMPLEMENTATION.md) - 前端详细实施文档
- [API 文档](./API_DOCUMENTATION.md) - 完整的 API 文档
- [DRF 实施总结](./DRF_IMPLEMENTATION_SUMMARY.md) - 后端实施总结
- [前端 README](./frontend/README.md) - 前端项目文档
