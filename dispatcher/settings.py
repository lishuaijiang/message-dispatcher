import os
from pathlib import Path

from aio_pika import ExchangeType
from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录
project_root = Path(__file__).parents[1]
env_file = project_root / ".env"
app_env = os.environ.get("APP_ENV", "development").lower()

if app_env == "development":
    if env_file.exists():
        print(f"✅ 已加载环境文件: {env_file.absolute()}")
    else:
        print("\033[33m ⚠️.env 文件不存在，将仅从系统环境变量中读取配置 \033[0m")


class Settings(BaseSettings):
    """
    负责在应用启动时从环境变量（及可选的 .env 文件）中读取并校验配置项，并以统一、类型安全
    的方式提供给应用各模块使用

    代替了 python-dotenv 的显式 load_env 以及 os.environ.get 操作
    """
    log_level: str = "INFO"
    rabbitmq_url: str | None = None
    connect_rabbitmq_retry_interval: int = 3
    connect_rabbitmq_timeout: int = 3
    connect_rabbitmq_max_retries: int = 5

    # 默认配置（当请求中未指定时使用）
    default_exchange_type: str = ExchangeType.TOPIC
    default_exchange_name: str = "dispatcher_exchange"
    default_queue_name: str = "dispatcher_queue"
    default_routing_key: str = "test_routing_key"

    # 是否自动创建 RabbitMQ 拓扑，默认为True
    auto_declare_rabbitmq_topology: bool = True

    # ref: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
    model_config = SettingsConfigDict(
        # 暂时不考虑使用前缀区分 Compose 环境变量和 Code 环境变量，后续可选使用前缀区分
        env_prefix="",
        env_file=env_file if app_env == "development" else ".env",
        env_file_encoding='utf-8',
        # 区分大小写
        case_sensitive=False,
    )


settings = Settings()

__all__ = ["settings"]
