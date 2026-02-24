#!/bin/bash
# Blog Backend 启动脚本

cd "$(dirname "$0")"

# 添加常见的用户bin目录到PATH
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "Error: uv not found. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 杀掉占用 8000 端口的进程
PID=$(lsof -ti:8000 2>/dev/null)
if [ -n "$PID" ]; then
    echo "Killing existing process on port 8000 (PID: $PID)..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# 同步依赖
echo "Syncing dependencies..."
uv sync

# 启动服务（后台运行，同时托管前端和后端）
echo "Starting server at http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo "Admin: http://localhost:8000/admin/login.html"
echo ""
nohup uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1 &
echo "Server started in background. PID: $!"
echo "Logs: $(pwd)/server.log"
