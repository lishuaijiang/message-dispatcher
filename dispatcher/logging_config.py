import logging
import sys


def setup_logging(
        level: str = "INFO",
        format_str: str | None = None,
        date_format: str | None = None
):
    """配置整个应用的日志系统，显式覆盖 logging 的默认配置，但不改变 logging 的使用方式"""
    root_logger = logging.getLogger()

    # 清除所有现有 handler（避免重复）
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 设置日志级别
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if format_str is None:
        format_str = "%(asctime)s [%(levelname)s %(filename)s:%(lineno)d] %(message)s"
    if date_format is None:
        date_format = "%m-%d %H:%M:%S"

    # 兼容本地开发输出到控制台 和 Compose 启动输出到日志文件
    # 1. 本地 IDE 直接打印到控制台
    # 2. Docker 自动收集日志到容器日志文件
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt=format_str,
        datefmt=date_format
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # 配置第三方库的日志级别
    # logging.getLogger("aio_pika").setLevel(logging.WARNING)
    # logging.getLogger("uvicorn").setLevel(logging.INFO)
    # logging.getLogger("fastapi").setLevel(logging.INFO)
