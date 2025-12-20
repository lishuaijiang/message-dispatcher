import logging
import json

from aio_pika import RobustChannel
from fastapi import APIRouter, Depends

from dispatcher.messaging.publisher import publish
from dispatcher.schemas import SubmitTaskIn
from dispatcher.utils import get_logger_dep, get_rabbitmq_channel

router = APIRouter(tags=["api"])


@router.post("/submit_task")
async def submit_task(
        task: SubmitTaskIn,
        logger: logging.Logger = Depends(get_logger_dep),
        channel: RobustChannel = Depends(get_rabbitmq_channel)
) -> dict:
    """提交任务到消息队列"""

    # 将任务数据序列化为 JSON bytes
    body = json.dumps(task.model_dump()).encode("utf-8")

    await publish(channel=channel, body=body)
    return {"task_id": task.id, "status": "submitted"}
