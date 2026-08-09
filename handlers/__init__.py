from aiogram import Router
from .admin import router as admin_router
from .start import router as start_router
from .help import router as help_router
from .booking import router as booking_router
from .callbacks import router as callbacks_router
from .my_appointments import router as my_appointments_router

router = Router()

router.include_router(start_router)
router.include_router(help_router)
router.include_router(booking_router)
router.include_router(callbacks_router)
router.include_router(my_appointments_router)
router.include_router(admin_router)