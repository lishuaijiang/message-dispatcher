from contextlib import asynccontextmanager

from aio_pika import connect_robust, ExchangeType
from aio_pika.abc import AbstractRobustConnection
from fastapi import FastAPI

from dispatcher.settings import settings


@asynccontextmanager
async def rabbitmq_lifespan(app: FastAPI):
    """
    RabbitMQ 应用生命周期管理函数

    该函数作为 FastAPI 的 lifespan 回调，在 FastAPI 应用启动时建立RabbitMQ 连接，
    并在 FastAPI 应用关闭时负责资源的安全释放
    """

    if not settings.rabbitmq_url:
        raise RuntimeError("rabbitmq_url 未配置")

    connection: AbstractRobustConnection = await connect_robust(
        settings.rabbitmq_url)

    # 初始化 broker 结构（声明交换机和队列）
    async with connection.channel() as channel:
        exchange = await channel.declare_exchange(
            settings.exchange_name, ExchangeType.DIRECT, durable=True
        )
        queue = await channel.declare_queue(
            settings.queue_name, durable=True
        )

        await queue.bind(exchange, routing_key=settings.routing_key)

    app.state.rabbitmq_connection = connection

    try:
        yield
    finally:
        if not connection.is_closed:
            await connection.close()
