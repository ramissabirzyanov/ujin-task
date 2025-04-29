import uvicorn
from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.core.setup_parser import setup_parser
from app.api.middlewares import debug_logging_middleware


def create_app():
    app = FastAPI()
    parsed_args = setup_parser()
    app.state.parsed_args = parsed_args
    app.middleware("http")(debug_logging_middleware)
    app.include_router(api_router, prefix='/api')

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
