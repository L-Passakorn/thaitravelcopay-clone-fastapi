from fastapi import APIRouter
from . import (
    authentication_router,
    user_router,
    hello_router,
)

router = APIRouter(prefix="/v1")
router.include_router(authentication_router.router)
router.include_router(user_router.router)

# add test router to v1
from . import hello_router

router.include_router(hello_router.router)
