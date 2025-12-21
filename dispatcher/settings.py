import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from dispatcher.utils import get_logger

_logger = get_logger(name="dispatcher.settings", level=logging.DEBUG)

# 项目根目录
BASE_DIR = Path(__file__).parents[1]
local_env = BASE_DIR / ".env"

if local_env.exists():
    env_file = local_env
else:
    env_file = None
    _logger.warning("\033[33m ⚠️.env 文件不存在，将仅从系统环境变量中读取配置 \033[0m")


class Settings(BaseSettings):
    """
    负责在应用启动时从环境变量（及可选的 .env 文件）中读取并校验配置项，并以统一、类型安全
    的方式提供给应用各模块使用

    代替了 python-dotenv 的显式 load_env 以及 os.environ.get 操作
    """
    log_level: str = "INFO"
    rabbitmq_url: str | None = None
    exchange_name: str = "dispatcher_exchange"
    queue_name: str = "dispatcher_queue"
    routing_key: str = "test.key"

    model_config = SettingsConfigDict(
        # 暂时不考虑使用前缀区分 Compose 环境变量和 Code 环境变量，后续可选使用前缀区分
        env_prefix="",
        env_file=env_file,
        # 区分大小写
        case_sensitive=False,
    )

    @property
    def resolved_log_level(self) -> int:
        """将字符串日志等级统一转为 logging 模块的 int 值"""
        level = self.log_level.upper()
        return getattr(logging, level, logging.INFO)


settings = Settings()

__all__ = ["settings"]
