from aio_pika import RobustChannel
from fastapi import APIRouter, Depends

from dispatcher.utils import get_rabbitmq_channel

router = APIRouter(tags=["health"])


@router.get("/")
@router.get("/health")
def health(
    channel: RobustChannel = Depends(get_rabbitmq_channel)
) -> dict:
    """
    健康检查
    - API 存活
    - RabbitMQ 连接是否可用（主要是测试 rabbitmq 的连接配置是否正确）
    """
    api_ok = True

    try:
        rabbitmq_ok = channel is not None and not channel.is_closed
        rabbitmq_detail = "连接正常" if rabbitmq_ok else "连接已关闭"
    except Exception as e:
        rabbitmq_ok = False
        rabbitmq_detail = f"连接异常: {e}"

    # 总体状态
    overall_status = "ok" if api_ok and rabbitmq_ok else "degraded"

    return {
        "overall_status": overall_status,
        "services": {
            "api": {"status": api_ok, "detail": "API 服务可用"},
            "rabbitmq": {"status": rabbitmq_ok, "detail": rabbitmq_detail},
        }
    }
