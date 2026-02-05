#!/bin/bash
# Blog Backend 启动脚本

cd "$(dirname "$0")"

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "Error: uv not found. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 杀掉占用 8000 端口的进程
PORT=8000
PID=$(lsof -ti:$PORT 2>/dev/null)
if [ -n "$PID" ]; then
    echo "Killing existing process on port $PORT (PID: $PID)..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# 同步依赖
echo "Syncing dependencies..."
uv sync

# 启动服务
echo "Starting server at http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo "Admin: http://localhost:8000/admin/login.html"
echo ""
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
