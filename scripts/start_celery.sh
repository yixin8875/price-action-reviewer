#!/bin/bash

# Celery Worker 和 Beat 启动脚本

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Celery 启动脚本 ===${NC}"

# 检查 Redis 是否运行
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}错误: Redis 未运行，请先启动 Redis${NC}"
    echo "启动命令: redis-server"
    exit 1
fi

echo -e "${GREEN}Redis 运行正常${NC}"

# 启动模式选择
case "$1" in
    worker)
        echo -e "${YELLOW}启动 Celery Worker...${NC}"
        celery -A config worker -l info
        ;;
    beat)
        echo -e "${YELLOW}启动 Celery Beat (定时任务调度器)...${NC}"
        celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    both)
        echo -e "${YELLOW}同时启动 Worker 和 Beat...${NC}"
        celery -A config worker -B -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    flower)
        echo -e "${YELLOW}启动 Flower (监控界面)...${NC}"
        celery -A config flower
        ;;
    *)
        echo "用法: $0 {worker|beat|both|flower}"
        echo ""
        echo "  worker  - 启动 Celery Worker（执行任务）"
        echo "  beat    - 启动 Celery Beat（定时任务调度）"
        echo "  both    - 同时启动 Worker 和 Beat"
        echo "  flower  - 启动 Flower 监控界面"
        echo ""
        echo "示例:"
        echo "  $0 worker    # 启动 worker"
        echo "  $0 beat      # 启动 beat"
        echo "  $0 both      # 同时启动（开发环境）"
        exit 1
        ;;
esac
