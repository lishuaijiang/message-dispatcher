from dispatcher.factory_app import create_app
from dispatcher.logging_config import setup_logging
from dispatcher.settings import settings

setup_logging(level=settings.log_level)
app = create_app()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("dispatcher.main:app", host="0.0.0.0", port=8000)
