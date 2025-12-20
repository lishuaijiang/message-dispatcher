from fastapi import FastAPI

from dispatcher.messaging.lifespan import rabbitmq_lifespan
from dispatcher.routers import api, health
from dispatcher.settings import settings
from dispatcher.utils import get_logger


def create_app() -> FastAPI:
    # 实例化 FastAPI，并将 RabbitMQ 的生命周期交由 FastAPI 管理
    app = FastAPI(lifespan=rabbitmq_lifespan)

    # 路由注册
    app.include_router(health.router)
    app.include_router(api.router, prefix="/api/v1")

    # 绑定 logger
    app.logger = get_logger(
        name="dispatcher_app",
        level=settings.resolved_log_level,
    )
    return app
