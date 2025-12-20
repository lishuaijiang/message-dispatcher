import logging
import sys

from aio_pika import RobustChannel
from fastapi import Request


def get_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        # 兼容本地开发输出到控制台 和 Compose 启动输出到日志文件
        # 1. 本地 IDE 直接打印到控制台
        # 2. Docker 自动收集日志到容器日志文件
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s %(filename)s:%(lineno)d] %(message)s",
            datefmt="%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger


async def get_rabbitmq_channel(request: Request) -> RobustChannel:
    """随用随取，避免在 lifespan 中挂载到 app 上，出现全局唯一 channel 问题"""
    connection = request.app.state.rabbitmq_connection

    channel: RobustChannel = None
    try:
        channel = await connection.channel()
        yield channel
    finally:
        if channel and not channel.is_closed:
            await channel.close()


def get_logger_dep(request: Request) -> logging.Logger:
    return request.app.logger
