from pathlib import Path

from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig
from litestar.config.compression import CompressionConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.datastructures import CacheControlHeader
from litestar.logging import LoggingConfig
from litestar.plugins.flash import FlashConfig
from litestar.template import TemplateConfig
from litestar_vite import ViteConfig
from litestar_vite.plugin import StaticFilesConfig
from sqlalchemy.ext.asyncio import create_async_engine

from app import settings
from app.models import Base

engine = create_async_engine(
    url=settings.db.URL,
    echo=settings.db.ECHO,
)

sqlalchemy_config = SQLAlchemyAsyncConfig(
    create_all=True,
    metadata=Base.metadata,
    before_send_handler="autocommit",
    engine_instance=engine,
)

template_config = TemplateConfig(
    directory=Path(__file__).parent / "templates",
    engine=JinjaTemplateEngine,
)

flush_config = FlashConfig(template_config=template_config)

logging_config = LoggingConfig(
    root={
        "level": settings.log.LEVEL,
        "handlers": ["queue_listener"],
    },
    formatters={
        "standard": {"format": "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"}
    },
    log_exceptions="debug",
    loggers={
        "sqlalchemy.engine": {
            "propagate": False,
            "level": settings.log.SQLALCHEMY_LEVEL,
            "handlers": ["queue_listener"],
        },
        "sqlalchemy.pool": {
            "propagate": False,
            "level": settings.log.SQLALCHEMY_LEVEL,
            "handlers": ["queue_listener"],
        },
    },
)

compression_config = CompressionConfig(
    backend="gzip",
    gzip_compress_level=9,
)

vite_config = ViteConfig(
    use_server_lifespan=settings.vite.USE_SERVER_LIFETIME,
    dev_mode=settings.vite.DEV_MODE,
)

vite_static_files_config = StaticFilesConfig(
    cache_control=CacheControlHeader(max_age=3600),
)

assets_path = Path(__file__).resolve().parent.parent / "storage" / "assets"
sessions_path = Path(__file__).resolve().parent.parent / "storage" / "sessions"
