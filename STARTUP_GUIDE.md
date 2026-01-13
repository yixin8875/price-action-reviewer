# 价格行为复盘系统 - 启动指南

## 项目架构

- **后端**: Django 5.0 + Django REST Framework（端口：8000）
- **前端**: React 18 + TypeScript + Material-UI（端口：5173）
- **数据库**: SQLite（开发环境）
- **异步任务**: Celery + Redis

---

## 快速启动（3 步）

### 1️⃣ 启动后端 API

```bash
# 进入项目根目录
cd /Users/boohee/Documents/trae_projects/price-action-reviewer

# 激活虚拟环境
source .venv/bin/activate

# 运行数据库迁移（首次启动）
python manage.py migrate

# 创建测试用户和数据（首次启动）
python scripts/setup_api.py

# 启动 Django 开发服务器
python manage.py runserver
```

**后端访问地址**：
- API 文档：http://localhost:8000/api/v1/docs/
- API Schema：http://localhost:8000/api/v1/schema/

### 2️⃣ 启动前端应用

```bash
# 打开新终端窗口
cd /Users/boohee/Documents/trae_projects/price-action-reviewer/frontend

# 安装依赖（首次启动）
npm install

# 启动开发服务器
npm run dev
```

**前端访问地址**：
- 应用首页：http://localhost:5173

### 3️⃣ 登录系统

**测试账号**：
- 用户名：`testuser`
- 密码：`testpass123`

---

## 详细启动步骤

### 前置要求

- Python 3.11+
- Node.js 18+
- Redis（可选，用于 Celery）

### 后端启动详细步骤

#### 1. 检查虚拟环境

```bash
cd /Users/boohee/Documents/trae_projects/price-action-reviewer

# 检查虚拟环境是否存在
ls .venv

# 如果不存在，创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate
```

#### 2. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt
```

#### 3. 数据库初始化

```bash
# 运行数据库迁移
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser
```

#### 4. 创建测试数据

```bash
# 运行测试脚本（创建测试用户和示例数据）
python scripts/setup_api.py
```

这个脚本会：
- 创建测试用户（testuser / testpass123）
- 创建示例标的（600000 浦发银行、000001 平安银行）
- 创建示例复盘记录

#### 5. 启动开发服务器

```bash
# 启动 Django 服务器
python manage.py runserver

# 或指定端口
python manage.py runserver 8000
```

#### 6. 验证后端运行

访问 http://localhost:8000/api/v1/docs/ 查看 API 文档

### 前端启动详细步骤

#### 1. 安装依赖

```bash
cd /Users/boohee/Documents/trae_projects/price-action-reviewer/frontend

# 安装 npm 依赖
npm install
```

#### 2. 配置环境变量

检查 `.env` 文件是否存在：

```bash
cat .env
```

应该包含：
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

#### 3. 启动开发服务器

```bash
# 启动 Vite 开发服务器
npm run dev
```

#### 4. 访问应用

打开浏览器访问：http://localhost:5173

---

## 启动 Celery（可选）

如果需要使用异步任务功能（批量数据同步、技术指标计算）：

### 1. 启动 Redis

```bash
# macOS (使用 Homebrew)
brew services start redis

# 或直接运行
redis-server
```

### 2. 启动 Celery Worker

```bash
# 在项目根目录，新开一个终端
cd /Users/boohee/Documents/trae_projects/price-action-reviewer
source .venv/bin/activate

# 启动 Celery worker
celery -A config worker -l info
```

### 3. 启动 Celery Beat（定时任务）

```bash
# 新开一个终端
cd /Users/boohee/Documents/trae_projects/price-action-reviewer
source .venv/bin/activate

# 启动 Celery beat
celery -A config beat -l info
```

---

## 常见问题

### 1. 端口被占用

**问题**：`Error: That port is already in use.`

**解决**：
```bash
# 查找占用端口的进程
lsof -ti:8000  # 后端
lsof -ti:5173  # 前端

# 杀死进程
kill -9 $(lsof -ti:8000)
```

### 2. 数据库迁移错误

**问题**：`no such table: xxx`

**解决**：
```bash
# 删除数据库（开发环境）
rm db.sqlite3

# 重新运行迁移
python manage.py migrate

# 重新创建测试数据
python scripts/setup_api.py
```

### 3. 前端依赖安装失败

**问题**：`npm install` 失败

**解决**：
```bash
# 清除 npm 缓存
npm cache clean --force

# 删除 node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 4. CORS 错误

**问题**：前端无法访问后端 API

**解决**：
- 检查后端是否运行在 http://localhost:8000
- 检查前端 `.env` 文件中的 `VITE_API_BASE_URL`
- 确保后端 CORS 配置正确（已在 settings.py 中配置）

### 5. JWT Token 过期

**问题**：登录后一段时间无法访问 API

**解决**：
- Access Token 有效期：1 小时
- Refresh Token 有效期：7 天
- 前端会自动刷新 Token，如果失败会重定向到登录页

---

## 开发工作流

### 日常开发

1. **启动后端**：
   ```bash
   cd /Users/boohee/Documents/trae_projects/price-action-reviewer
   source .venv/bin/activate
   python manage.py runserver
   ```

2. **启动前端**：
   ```bash
   cd /Users/boohee/Documents/trae_projects/price-action-reviewer/frontend
   npm run dev
   ```

3. **开发**：
   - 后端代码修改后自动重载
   - 前端代码修改后自动热更新

### 数据库管理

```bash
# 创建新的迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 查看迁移状态
python manage.py showmigrations

# 进入 Django shell
python manage.py shell
```

### 前端构建

```bash
cd frontend

# 开发模式
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview
```

---

## 项目结构

```
price-action-reviewer/
├── apps/                    # Django 应用
│   ├── api/                # API 路由配置
│   ├── market_data/        # 市场数据（标的、K线）
│   ├── technical_analysis/ # 技术分析（指标、形态）
│   └── review/             # 复盘记录
├── config/                 # Django 配置
│   ├── settings/           # 设置文件
│   └── urls.py            # 主路由
├── frontend/               # React 前端
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── pages/         # 页面
│   │   ├── services/      # API 服务
│   │   └── stores/        # 状态管理
│   └── package.json
├── scripts/                # 工具脚本
│   └── setup_api.py       # 测试数据脚本
├── manage.py              # Django 管理脚本
└── requirements.txt       # Python 依赖
```

---

## 功能概览

### 已实现功能

1. ✅ **用户认证**：JWT Token 认证，自动刷新
2. ✅ **Dashboard**：系统概览、统计数据、快捷操作
3. ✅ **标的管理**：CRUD 操作、批量同步数据
4. ✅ **K线图表**：ECharts 图表、技术指标叠加
5. ✅ **复盘记录**：创建/编辑复盘、评分、标签
6. ✅ **技术指标**：批量计算、指标管理
7. ✅ **移动端优化**：响应式布局、底部导航
8. ✅ **用户体验**：加载骨架屏、错误边界、表单验证

### API 端点

- `/api/v1/auth/login/` - 登录
- `/api/v1/auth/refresh/` - 刷新 Token
- `/api/v1/instruments/` - 标的管理
- `/api/v1/klines/` - K线数据
- `/api/v1/indicators/` - 技术指标
- `/api/v1/patterns/` - 形态识别
- `/api/v1/reviews/` - 复盘记录
- `/api/v1/trades/` - 交易日志

---

## 下一步

1. 登录系统：http://localhost:5173
2. 查看 Dashboard
3. 添加标的
4. 同步市场数据
5. 计算技术指标
6. 创建复盘记录
7. 查看 K线图表

---

## 技术支持

- API 文档：http://localhost:8000/api/v1/docs/
- 项目文档：查看项目根目录的 Markdown 文件
- 问题反馈：GitHub Issues

---

**祝你使用愉快！** 🚀
