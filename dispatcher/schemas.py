import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from dispatcher.settings import settings


class ExchangeTypeEnum(str, Enum):
    """Exchange 类型"""
    FANOUT = "fanout"
    DIRECT = "direct"
    TOPIC = "topic"
    HEADERS = "headers"


class SubmitTaskIn(BaseModel):
    """提交任务序列化器"""
    uuid: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="系统生成的唯一任务标识符，用于在RabbitMQ中追踪和定位该任务"
    )
    exchange_type: ExchangeTypeEnum | None = Field(
        default=settings.default_exchange_type,
        description="交换机类型，不提供则使用默认"
    )
    exchange_name: str | None = Field(
        default=settings.default_exchange_name,
        description="交换机名称，不提供则使用默认"
    )
    queue_name: str | None = Field(
        default=settings.default_queue_name,
        description="队列名称，不提供则使用默认"
    )
    routing_key: str | None = Field(
        default=settings.default_routing_key,
        description="路由键，不提供则使用默认"
    )

    payload: dict = Field(
        default={"test_message": "Hello RabbitMQ!"},
        description="待发布的消息内容"
    )

    model_config = ConfigDict(
        use_enum_values=True
    )
