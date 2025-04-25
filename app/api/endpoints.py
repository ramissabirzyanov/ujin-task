from fastapi import APIRouter
from fastapi import Depends, HTTPException, status


from app.core.schemas import USD


router = APIRouter()


@router.get('/usd/get', response_model=USD)
async def get_usd():
    pass


@router.get('/amount/get', response_model=USD)
async def get_usd():
    pass
