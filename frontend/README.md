# 价格行为复盘系统 - 前端应用

基于 React 18 + TypeScript + Material-UI 的现代化前端应用。

## 技术栈

- **React 18** - 使用最新的 React 特性
- **TypeScript** - 类型安全
- **Material-UI v5** - Material Design 3 组件库
- **React Router v6** - 客户端路由
- **TanStack Query** - 服务端状态管理
- **Zustand** - 客户端状态管理
- **ECharts** - K线图表可视化
- **Axios** - HTTP 客户端
- **Vite** - 快速构建工具

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

`.env` 文件已创建，默认配置：

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:5173 启动。

### 4. 构建生产版本

```bash
npm run build
```

## 核心功能

### 1. 认证系统
- JWT Token 认证
- 自动 Token 刷新（401 错误时）
- 路由守卫（未登录重定向）
- 持久化登录状态（localStorage）

### 2. 布局系统
- 响应式侧边导航栏
- 顶部应用栏（用户信息、主题切换）
- 深色/浅色主题切换
- Material Design 3 设计规范

### 3. 页面功能

#### 仪表盘（Dashboard）
- 统计卡片（标的总数、复盘记录、交易日志）
- 实时数据展示

#### 标的管理（Instruments）
- 数据表格（MUI DataGrid）
- 分页、排序、过滤

#### K线图表（Charts）
- 左侧标的列表
- 右侧 ECharts K线图
- 成交量柱状图

#### 复盘记录（Reviews）
- 卡片网格展示
- 复盘详情展示

## API 集成

### Axios 拦截器

**请求拦截器**：自动添加 JWT Token 到 Authorization header

**响应拦截器**：401 错误时自动刷新 Token

### API 端点

- `POST /auth/login/` - 用户登录
- `POST /auth/refresh/` - 刷新 Token
- `GET /instruments/` - 获取标的列表
- `GET /klines/` - 获取 K线数据
- `GET /reviews/` - 获取复盘记录
- `GET /trades/` - 获取交易日志

## 注意事项

1. **后端 API 必须运行**：确保 Django 后端在 http://localhost:8000 运行
2. **CORS 配置**：后端需要配置 CORS 允许前端域名
3. **Token 存储**：JWT Token 存储在 localStorage

## 故障排查

### 登录失败
- 检查后端 API 是否运行
- 检查 `.env` 中的 API 地址
- 查看浏览器控制台错误信息

### 图表不显示
- 确保 K线数据格式正确
- 检查 ECharts 是否正确初始化

