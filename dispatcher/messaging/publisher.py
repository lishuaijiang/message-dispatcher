import logging
import uuid

from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractChannel
from aio_pika.exceptions import DeliveryError

from dispatcher.messaging.topology import ensure_topology

logger = logging.getLogger(name="messaging.publisher")


async def publish(
        channel: AbstractChannel,
        exchange_type: str,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        body: bytes,
        *,
        message_id: str = str(uuid.uuid4()),
        max_retries: int = 3,
        **message_kwargs
) -> bool:
    """
    动态发布消息到指定的交换机和队列

    :param channel: 通道对象
    :param exchange_type: 交换机类型
    :param exchange_name: 交换机名称
    :param queue_name: 队列名称
    :param routing_key: 消息路由键
    :param body: 消息体内容
    :param message_id: 消息唯一ID（consumer 去重的唯一锚点）
    :param max_retries: 最大重试次数
    :param message_kwargs: 其他消息属性 (如 priority, correlation_id 等)

    :return: 发布是否成功 (True/False)
    """

    exchange = await ensure_topology(
        channel,
        exchange_name=exchange_name,
        exchange_type=exchange_type,
        queue_name=queue_name,
        routing_key=routing_key,
    )

    # 创建持久化消息对象
    message = Message(
        body=body,
        message_id=message_id,
        delivery_mode=DeliveryMode.PERSISTENT,
        **message_kwargs
    )

    for attempt in range(1, max_retries + 1):
        try:
            await exchange.publish(
                message,
                routing_key=routing_key,
                # 如果消息无法被路由到任何队列，RabbitMQ 会通过异步回调通知生产者，而不是默默地丢弃消息
                mandatory=True
            )
            logger.debug(f"消息: {body}, 发布成功: {exchange_name}::{routing_key}")
            return True

        except DeliveryError as e:
            logger.error(
                f"消息: {body}, 无法路由: {exchange_name}::{routing_key}, 错误：{e}")
            return False

        except Exception as e:
            logger.warning(
                f"消息: {body}, 尝试({attempt}/{max_retries})发布失败: {exchange_name}::{routing_key}, 错误：{e}")

    logger.error(f"消息: {body}, 发布失败: {exchange_name}::{routing_key}")
    return False
