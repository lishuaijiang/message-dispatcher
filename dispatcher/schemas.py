import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from dispatcher.settings import settings
from dispatcher.utils import gen_sn


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

    # Pydantic V2 配置
    model_config = ConfigDict(
        use_enum_values=True,
        validate_default=True
    )

    @model_validator(mode='before')
    def ensure_sn_in_payload(cls, values):
        """
        向 payload 中自动添加 sn 字段，用于唯一标识任务
        保证消费者端幂等落库和 Redis 队列可靠
        """
        payload = values.get("payload") or {}
        if "sn" not in payload:
            payload["sn"] = gen_sn()
        values["payload"] = payload
        return values
