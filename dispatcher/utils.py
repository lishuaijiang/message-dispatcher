from aio_pika.abc import AbstractChannel
from fastapi import Request


async def get_rabbitmq_channel(request: Request) -> AbstractChannel:
    """随用随取，避免在 lifespan 中挂载到 app 上，出现全局唯一 channel 问题"""
    channel: AbstractChannel | None = None

    try:
        connection = request.app.state.rabbitmq_connection
        # 开启发布者确认模式，让 publisher 知道消息是否成功到达 MQ
        channel = await connection.channel(publisher_confirms=True)
        yield channel
    finally:
        if channel and not channel.is_closed:
            await channel.close()
