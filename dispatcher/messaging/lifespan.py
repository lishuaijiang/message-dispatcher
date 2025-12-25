import asyncio
import logging
from contextlib import asynccontextmanager

from aio_pika import connect_robust
from aio_pika.abc import AbstractConnection
from fastapi import FastAPI

from dispatcher.settings import settings

logger = logging.getLogger("messaging.lifespan")


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

    async def connect_loop() -> AbstractConnection:
        """为解决 RabbitMQ 的 health ≠ AMQP ready，即使通过了健康检查，5672端口未必就绪"""
        rabbitmq_url = settings.rabbitmq_url
        interval = settings.connect_rabbitmq_retry_interval
        timeout = settings.connect_rabbitmq_timeout
        max_retries = settings.connect_rabbitmq_max_retries

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"连接 RabbitMQ（第 {attempt} 次尝试）")
                conn = await asyncio.wait_for(
                    connect_robust(rabbitmq_url),
                    timeout=timeout
                )
                logger.info(f"连接 RabbitMQ 成功")
                return conn

            except Exception as e:
                logger.warning(f"连接 RabbitMQ 失败: {e}，等待 {interval} 秒后重试")
                await asyncio.sleep(interval)
        else:
            logger.critical(f"已尝试 {max_retries} 次，RabbitMQ 未就绪，API 服务启动中止")
            raise RuntimeError("RabbitMQ 连接失败，达到最大重试次数")

    try:
        connection = await connect_loop()
        app.state.rabbitmq_connection = connection
        yield
    finally:
        if connection and not connection.is_closed:
            await connection.close()
