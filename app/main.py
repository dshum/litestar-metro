from litestar import Litestar


def create_app() -> Litestar:
    from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
    from litestar.config.app import AppConfig
    from litestar.datastructures import CacheControlHeader
    from litestar.di import Provide
    from litestar.exceptions import (
        NotAuthorizedException,
        HTTPException,
        NotFoundException,
        ValidationException,
    )
    from litestar.plugins.flash import FlashPlugin
    from litestar.static_files import create_static_files_router
    from litestar.stores.file import FileStore
    from litestar_htmx import HTMXRequest
    from litestar_vite import VitePlugin

    from app import settings
    from app.configs import (
        compression_config,
        flush_config,
        logging_config,
        sqlalchemy_config,
        template_config,
        vite_config,
        vite_static_files_config,
        assets_path,
        data_path,
        screenshots_path,
        sessions_path,
    )
    from app.controllers import app_router
    from app.controllers.admin import admin_router
    from app.dependencies import provide_limit_offset_pagination
    from app.exceptions import (
        base_exception_handler,
        http_exception_handler,
        not_authorized_exception_handler,
        not_found_exception_handler,
        validation_exception_handler,
    )
    from app.guards import session_auth
    from app.plugins import CLIPlugin

    def create_folders(app_config: AppConfig) -> AppConfig:
        for path in [assets_path, screenshots_path, data_path, sessions_path]:
            path.mkdir(parents=True, exist_ok=True)
        return app_config

    return Litestar(
        route_handlers=[
            app_router,
            admin_router,
            create_static_files_router(
                cache_control=CacheControlHeader(max_age=3600),
                directories=[assets_path],
                path="/assets",
                name="assets",
            ),
        ],
        dependencies={
            "limit_offset": Provide(provide_limit_offset_pagination),
        },
        plugins=[
            CLIPlugin(),
            FlashPlugin(config=flush_config),
            SQLAlchemyPlugin(config=sqlalchemy_config),
            VitePlugin(
                config=vite_config,
                static_files_config=vite_static_files_config,
            ),
        ],
        on_app_init=[session_auth.on_app_init, create_folders],
        middleware=[session_auth.middleware],
        logging_config=logging_config,
        request_class=HTMXRequest,
        template_config=template_config,
        compression_config=compression_config,
        exception_handlers={
            NotFoundException: not_found_exception_handler,
            ValidationException: validation_exception_handler,
            NotAuthorizedException: not_authorized_exception_handler,
            HTTPException: http_exception_handler,
            BaseException: base_exception_handler,
        },
        stores={
            "sessions": FileStore(path=sessions_path),
        },
        request_max_body_size=settings.app.REQUEST_MAX_BODY_SIZE,
        debug=settings.app.DEBUG,
    )


app = create_app()
