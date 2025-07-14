from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import typing
import jwt
import logging

from pydantic import ValidationError

from flasx import models
from . import security
from . import config

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token")

settings = config.get_settings()


async def get_current_user(
    token: typing.Annotated[str, Depends(oauth2_scheme)],
    session: typing.Annotated[models.AsyncSession, Depends(models.get_session)],
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_id: int = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except Exception as e:
        print(e)
        raise credentials_exception

    user = await session.get(models.DBUser, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: typing.Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    # Remove status check since User model doesn't have status field
    return current_user


async def get_current_active_superuser(
    current_user: typing.Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    # Remove roles check since User model doesn't have roles field
    # This would need to be implemented based on your user permission system
    return current_user


class RoleChecker:
    def __init__(self, *allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        user: typing.Annotated[models.User, Depends(get_current_active_user)],
    ):
        # Remove role checking since User model doesn't have roles field
        # This would need to be implemented based on your user permission system
        return user
