from fastapi import APIRouter
from . import (
    authentication_router,
    registration_router,
    user_router,
    hello_router,
    province_router,
    user_province_router,
)

router = APIRouter(prefix="/v1")
router.include_router(authentication_router.router)
router.include_router(registration_router.router)
router.include_router(user_router.router)
router.include_router(hello_router.router)
router.include_router(province_router.router)
router.include_router(user_province_router.router)
