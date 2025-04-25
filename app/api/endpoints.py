from fastapi import APIRouter
from fastapi import Depends, HTTPException, status


from app.core.schemas import USDResponse


router = APIRouter()


@router.get('/usd/get', response_model=USDResponse)
async def get_usd():
    pass