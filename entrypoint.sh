#!/usr/bin/env bash
set -e

ACTION="${1:-launch}"
SERVER="${2:-dispatcher}"

if [ "$ACTION" = "launch" ]; then
    if [ "$SERVER" = "dispatcher" ]; then
        exec uvicorn dispatcher.main:app \
            --host 0.0.0.0 \
            --port 8000 \
            --workers "${WORKERS:-4}" \
            --log-level "${LOG_LEVEL:-info}"
    else
        echo "ERROR: Unknown launch target: $SERVER"
        exit 1
    fi

elif [ "$ACTION" = "help" ]; then
    echo "Usage:"
    echo "  launch dispatcher   启动 API 服务"
    exit 0

else
    # 兜底：允许直接执行任意命令
    exec "$@"
fi
