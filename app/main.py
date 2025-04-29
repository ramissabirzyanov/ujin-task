import asyncio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from httpx import RequestError

from app.api.endpoints import router as api_router
from app.core.setup_parser import setup_parser
from app.api.middlewares import debug_logging_middleware
from app.services.currency_service import CurrencyService
from app.services.rate_service import cbr_currency_rate
from app.core.logger import logger


async def update_rates_job(service: CurrencyService, period: int):
    """Фоновая задача для обновления курсов"""
    while True:
        await asyncio.sleep(period * 60)
        try:
            rates = await service.get_all_rates()
            print(f"\n==== Обновление курсов ====")
            for pair, rate in rates.items():
                print(f"{pair} = {rate}")
        except RequestError as e:
            logger.error(f"Can't get rate updates for {pair}")
            return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    args = setup_parser()
    app.state.cli_args = setup_parser()
    app.state.currency_service = CurrencyService(
        balance=app.state.cli_args.balance,
        data_source=cbr_currency_rate
    )

    app.state.update_task = asyncio.create_task(
        update_rates_job(
            service=app.state.currency_service,
            period=app.state.cli_args.period
        )
    )
    yield
    app.state.update_task.cancel()
    try:
        await app.state.update_task
    except asyncio.CancelledError:
        logger.info("We are done here")


app = FastAPI(lifespan=lifespan)
app.middleware("http")(debug_logging_middleware)
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
