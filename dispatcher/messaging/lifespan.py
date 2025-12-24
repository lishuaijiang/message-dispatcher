from contextlib import asynccontextmanager

from aio_pika import connect_robust
from aio_pika.abc import AbstractConnection
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

    connection: AbstractConnection | None = None

    try:
        connection = await connect_robust(settings.rabbitmq_url)
        app.state.rabbitmq_connection = connection
        yield
    finally:
        if connection and not connection.is_closed:
            await connection.close()
