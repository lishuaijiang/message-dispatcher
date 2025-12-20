from pydantic import BaseModel


class SubmitTaskIn(BaseModel):
    """提交任务的输入模型"""
    id: str = "123123"
    message: str = "hello rabbitmq"
