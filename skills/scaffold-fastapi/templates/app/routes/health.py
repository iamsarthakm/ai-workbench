from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, ping_database
from app.middleware.log import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def health_live():
    """Liveness: process is up. No dependency checks."""
    return {"status": "ok"}


@router.get("/health/ready")
async def health_ready(response: Response, db: AsyncSession = Depends(get_db)):
    """Readiness: can serve traffic (database reachable)."""
    try:
        await ping_database(db)
    except Exception:
        logger.error("Readiness check failed: database unreachable", exc_info=True)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable", "checks": {"database": "fail"}}
    return {"status": "ok", "checks": {"database": "ok"}}
