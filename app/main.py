import uvicorn
from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.core.setup_parser import setup_parser
from app.api.dependencies import set_parsed_args, is_debug


app = FastAPI()
app.include_router(api_router, prefix='/api')


if __name__ == "__main__":
    args = setup_parser()
    set_parsed_args(args)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
