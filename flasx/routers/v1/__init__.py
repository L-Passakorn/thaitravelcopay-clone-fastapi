from fastapi import APIRouter
from . import (
    customer_router,
    station_router,
    vehicle_router,
    delivery_staff_router,
    parcel_router,
    authentication_router,
    user_router,
    hello_router,
)

router = APIRouter(prefix="/v1")
router.include_router(customer_router.router)
router.include_router(station_router.router)
router.include_router(vehicle_router.router)
router.include_router(delivery_staff_router.router)
router.include_router(parcel_router.router)
router.include_router(authentication_router.router)
router.include_router(user_router.router)

# add test router to v1
from . import hello_router

router.include_router(hello_router.router)
