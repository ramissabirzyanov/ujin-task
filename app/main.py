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
        try:
            rates = await service.get_all_rates()
            print("\n==== Обновление курсов ====")
            for pair, rate in rates.items():
                print(f"{pair} = {rate}")
        except RequestError:
            logger.error(f"Can't get rate updates for {pair}")
        await asyncio.sleep(period * 60)

async def monitor_changes(service: CurrencyService):
    """Фоновая задача для мониторинга изменений"""
    last_data = None
    
    while True:
        current_data = await service.get_total_amount()
        
        if current_data != last_data and last_data is not None:
            print("\n==== Появились изменения ====")
            balance = service.balance
            rates = await service.get_all_rates()
            sum_to_print = "sum: " + " / ".join([f"{value} {currency}" for currency, value in current_data])
            for currency, amount in balance.items():
                print(f"{currency}: {amount}")
            print("\n")
            for pair, rate in rates.items():
                print(f"{pair}: {rate}")
            print("\n")
            print(sum_to_print)
            print("\n")
            last_data = current_data

        await asyncio.sleep(60) 

            
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.cli_args = setup_parser()
    app.state.currency_service = CurrencyService(
        balance=app.state.cli_args.balance,
        data_source=cbr_currency_rate
    )

    update_task = asyncio.create_task(
        update_rates_job(
            service=app.state.currency_service,
            period=app.state.cli_args.period
        )
    )
    monitor_task = asyncio.create_task(
        monitor_changes(service=app.state.currency_service))

    app.state.update_task = update_task
    app.state.monitor_task = monitor_task

    try:
        yield
    finally:

        update_task.cancel()
        monitor_task.cancel()
        await asyncio.gather(update_task, monitor_task, return_exceptions=True)
        logger.info("We are done here!")



app = FastAPI(lifespan=lifespan)
app.middleware("http")(debug_logging_middleware)
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
