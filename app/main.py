import asyncio
from contextlib import asynccontextmanager

import config
from api import router
from fastapi import FastAPI
from patisson_appLauncher.fastapi_app_launcher import UvicornFastapiAppLauncher
from patisson_request.service_routes import InternalMediaRoute


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(config.SelfService.tokens_update_task())
    yield
    task.cancel()
    await task

app = FastAPI(title=config.SERVICE_NAME, lifespan=lifespan)

if __name__ == "__main__":
    health_path = f'/{config.SERVICE_NAME}/{InternalMediaRoute.health().path}'
    
    app_launcher = UvicornFastapiAppLauncher(app, router,
                        service_name=config.SERVICE_NAME,
                        host=config.SERVICE_HOST)
    app_launcher.add_token_middleware(
        config.SelfService.get_access_token,
        excluded_paths=[health_path]
        )
    app_launcher.add_sync_consul_health_path()
    app_launcher.consul_register(health_path)
    app_launcher.add_jaeger()
    app_launcher.include_router(prefix=f'/{config.SERVICE_NAME}')
    app_launcher.app_run()