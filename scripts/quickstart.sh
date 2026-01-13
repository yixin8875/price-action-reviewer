#!/bin/bash

# 价格行为复盘系统 - 快速启动脚本
# 用于首次安装和启动系统

set -e  # 遇到错误立即退出

echo "=========================================="
echo "价格行为复盘专家系统 - 快速启动"
echo "=========================================="
echo ""

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "当前 Python 版本: $python_version"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "创建虚拟环境..."
    python -m venv venv
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate
echo "✓ 虚拟环境已激活"

# 安装依赖
echo ""
echo "安装 Python 依赖包..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ 依赖包安装完成"

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo ""
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "✓ .env 文件已创建"
fi

# 运行数据库迁移
echo ""
echo "运行数据库迁移..."
python manage.py makemigrations
python manage.py migrate
echo "✓ 数据库迁移完成"

# 检查是否已创建超级用户
echo ""
read -p "是否需要创建超级用户？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# 询问是否同步数据
echo ""
read -p "是否同步股票数据（前10只）？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "同步股票列表..."
    python manage.py sync_data --sync-list --type stock
    echo "✓ 股票列表同步完成"
fi

# 检查 Redis
echo ""
echo "检查 Redis 服务..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis 正在运行"
    redis_running=true
else
    echo "⚠ Redis 未运行"
    echo "提示：如需使用定时任务功能，请先启动 Redis："
    echo "  macOS: brew install redis && redis-server"
    echo "  Linux: sudo apt-get install redis-server && redis-server"
    redis_running=false
fi

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "启动方式："
echo ""
echo "1. 启动 Django 开发服务器："
echo "   python manage.py runserver"
echo "   访问: http://127.0.0.1:8000/admin/"
echo ""

if [ "$redis_running" = true ]; then
    echo "2. 启动 Celery（可选，用于定时任务）："
    echo "   ./scripts/start_celery.sh both"
    echo ""
fi

echo "常用命令："
echo "  - 同步数据: python manage.py sync_data --symbol 600000 --days 30"
echo "  - 计算指标: python manage.py calculate_indicators --symbol 600000"
echo "  - 创建复盘: python manage.py create_review --symbol 600000"
echo ""
echo "详细文档请查看 README.md"
echo ""
