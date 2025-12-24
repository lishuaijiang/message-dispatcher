import json

from aio_pika.abc import AbstractChannel
from fastapi import APIRouter, Depends

from dispatcher.messaging.publisher import publish
from dispatcher.schemas import SubmitTaskIn
from dispatcher.utils import get_rabbitmq_channel

router = APIRouter(tags=["api"])


@router.post("/submit_task")
async def submit_task(
        task: SubmitTaskIn,
        channel: AbstractChannel = Depends(get_rabbitmq_channel)
) -> dict:
    """提交任务到消息队列（支持动态交换机和队列）"""
    task_dict = task.model_dump()

    # 分离队列配置参数和业务数据
    queue_config = {
        "exchange_type": task_dict.pop("exchange_type"),
        "exchange_name": task_dict.pop("exchange_name"),
        "queue_name": task_dict.pop("queue_name"),
        # 与 Dify 智能体约定好，传递 dify_agent.recognition_task 的 routing_key
        "routing_key": task_dict.pop("routing_key"),
    }

    message_id = task_dict.get("uuid")
    # 将任务数据序列化为 JSON bytes
    body = json.dumps(task_dict).encode("utf-8")

    # 动态发布消息
    await publish(
        channel=channel,
        body=body,
        message_id=message_id,
        **queue_config
    )
    return {"task_id": task.uuid, "status": "submitted"}
