"""
RabbitMQ 拓扑管理，负责 RabbitMQ 的拓扑结构（Exchange、Queue、Binging）的生命周期管理

uvicorn 多 worker 场景下，每个 worker 都会执行 declare 声明，但RabbitMQ 的
declare_exchange / declare_queue 是幂等的，实际资源只会创建一次，不会重复占用交换机或队列
"""

from aio_pika import ExchangeType
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractQueue

from dispatcher.settings import settings


async def _ensure_exchange(
        channel: AbstractChannel,
        *,
        name: str,
        type: str,
        durable: bool = True,
        auto_delete=False
) -> AbstractExchange:
    """
    确保 Exchange 存在并返回 Exchange 对象（幂等）
    """
    return await channel.declare_exchange(
        name=name,
        type=ExchangeType(type),
        durable=durable,
        auto_delete=auto_delete
    )


async def _ensure_queue(
        channel: AbstractChannel,
        *,
        name: str,
        durable: bool = True,
        auto_delete: bool = False,
        max_priority: int | None = None,
) -> AbstractQueue:
    """
    确保 Queue 存在并返回 Queue 对象，（幂等）
    """
    arguments = {}
    if max_priority is not None:
        arguments["x-max-priority"] = max_priority

    return await channel.declare_queue(
        name=name,
        durable=durable,
        auto_delete=auto_delete,
        arguments=arguments or None,
    )


async def _ensure_binding(
        *,
        exchange: AbstractExchange,
        queue: AbstractQueue,
        routing_key: str
) -> None:
    """
    确保 Queue 已绑定到 Exchange（幂等）
    """
    await queue.bind(exchange, routing_key=routing_key)


async def ensure_topology(
        channel: AbstractChannel,
        *,
        exchange_name: str,
        exchange_type: str,
        queue_name: str,
        routing_key: str,
        max_priority: int = 10,
) -> AbstractExchange:
    """
    RabbitMQ 拓扑管理，确保 Exchange、Queue、Binging 存在

    当 auto_declare_rabbitmq_topology=False 时：
    不再自动创建 RabbitMQ 拓扑，只能使用已经存在的拓扑，如果 Exchange 不存在则报错
    """
    #
    if not settings.auto_declare_rabbitmq_topology:
        return await channel.get_exchange(exchange_name)

    exchange = await _ensure_exchange(
        channel,
        name=exchange_name,
        type=exchange_type
    )
    queue = await _ensure_queue(
        channel,
        name=queue_name,
        max_priority=max_priority,
    )
    await _ensure_binding(
        exchange=exchange,
        queue=queue,
        routing_key=routing_key
    )

    return exchange

__all__ = ["ensure_topology"]
