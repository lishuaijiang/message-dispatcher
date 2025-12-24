from aio_pika.abc import AbstractChannel
from fastapi import APIRouter, Depends

from dispatcher.utils import get_rabbitmq_channel

router = APIRouter(tags=["health"])


@router.get("/")
@router.get("/health")
def health(
    channel: AbstractChannel = Depends(get_rabbitmq_channel)
) -> dict:
    """
    健康检查

    - API 是否可响应
    - RabbitMQ 连接是否可用（用于验证配置与基础依赖）
    """

    rabbitmq_ok = False

    try:
        if channel and not channel.is_closed:
            rabbitmq_ok = True
            rabbitmq_detail = "连接正常"
        else:
            rabbitmq_detail = "连接不可用或已关闭"
    except Exception as e:
        rabbitmq_detail = f"连接检查异常: {e}"

    overall_status = "ok" if rabbitmq_ok else "degraded"

    return {
        "overall_status": overall_status,
        "services": {
            "api": {
                "status": True,
                "detail": "API 服务可用"
            },
            "rabbitmq": {
                "status": rabbitmq_ok,
                "detail": rabbitmq_detail
            }
        }
    }
