"""
RabbitMQ 测试消费者，每次运行消费一条消息
因为是测试脚本，这里先不做 redis 消息去重（避免重复消费）
"""
import pika


def main(rabbitmq_url, exchange_name, exchange_type, queue_name, routing_key):
    # 建立连接
    params = pika.URLParameters(rabbitmq_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # 一个 consumer 同时最多拿几条未 ACK 的消息
    channel.basic_qos(prefetch_count=1)

    # 获取/声明交换机和队列
    channel.exchange_declare(
        exchange=exchange_name, exchange_type=exchange_type, durable=True)
    channel.queue_declare(queue=queue_name, durable=True)

    # 绑定队列到交换机上
    channel.queue_bind(
        queue=queue_name, exchange=exchange_name, routing_key=routing_key)

    # ref: https://pika.readthedocs.io/en/stable/examples/blocking_basic_get.html
    method_frame, header_frame, body = channel.basic_get(
        queue=queue_name, auto_ack=False)

    if not method_frame:
        print("队列中没有消息")
        connection.close()
        return

    if not body:
        print("收到空消息，跳过处理")
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        return

    try:
        print(f"收到消息: {body.decode('utf-8')}")

        # 手动确认
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    except Exception as e:
        print(f"处理消息失败: {e}")
        channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)
    finally:
        connection.close()


if __name__ == '__main__':
    main(
        rabbitmq_url="amqp://user:password@host:rabbitmq_server_port",
        exchange_name="dispatcher_exchange",
        exchange_type="topic",
        queue_name="dispatcher_queue",
        routing_key="test_routing_key"
    )
