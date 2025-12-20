import logging

from aio_pika import RobustChannel
from aio_pika.exceptions import DeliveryError
from aio_pika import DeliveryMode, Message

from dispatcher.settings import settings
from dispatcher.utils import get_logger

_logger = get_logger(name="messaging.publisher", level=logging.DEBUG)


async def publish(
        channel: RobustChannel,
        exchange_name: str = settings.exchange_name,
        routing_key: str = settings.routing_key,
        body: bytes = b"Hello RabbitMQ!",
        *,
        max_retries: int = 3,
        **message_kwargs
) -> bool:
    """
    发布消息到 RabbitMQ 交换机

    :param channel: 通道对象
    :param exchange_name: 交换机名称
    :param routing_key: 消息路由键
    :param body: 消息体内容 (bytes)
    :param max_retries: 最大重试次数 (默认 3)
    :param message_kwargs: 其他消息属性 (如 priority, correlation_id 等)
    :return: 发布是否成功 (True/False)
    """

    # 创建消息对象（持久化）
    message = Message(
        body=body,
        delivery_mode=DeliveryMode.PERSISTENT,
        **message_kwargs
    )

    for attempt in range(1, max_retries + 1):
        try:
            # 获取已经声明好的交换机
            exchange = await channel.get_exchange(exchange_name)

            await exchange.publish(
                message,
                routing_key=routing_key,
                # 确保消息被路由到队列
                mandatory=True
            )
            _logger.debug(f"消息: {body}, 成功发布到 {exchange_name}::{routing_key}")
            return True

        except DeliveryError as e:
            _logger.error(f"消息: {body}, 路由出错: {e}")
            return False

        except Exception as e:
            _logger.warning(f"消息发布失败 (尝试 {attempt}/{max_retries}): {str(e)}")
            if attempt == max_retries:
                _logger.error(f"无法发布消息到 {exchange_name}::{routing_key}: {str(e)}")
                return False
