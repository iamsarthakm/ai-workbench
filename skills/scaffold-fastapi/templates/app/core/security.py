"""JWT bearer auth: issue/verify tokens and resolve the current user from a request."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

ALGORITHM = "HS256"
auth_scheme = HTTPBearer()


def create_access_token(user_id: int, expires_minutes: int | None = None) -> str:
    """Issue a signed JWT for `user_id`. Wire this into your login/registration
    flow — this scaffold only provides the primitive."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
        if expires_minutes is not None
        else settings.JWT_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """Decode and validate a JWT, returning the user id from its subject claim."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        return int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid user id in token")


def get_current_user(auth: HTTPAuthorizationCredentials = Security(auth_scheme)) -> int:
    """FastAPI dependency: resolve the current user id from a Bearer JWT.

    Usage: `user_id: int = Depends(get_current_user)` on any route that requires auth.
    """
    return decode_access_token(auth.credentials)
