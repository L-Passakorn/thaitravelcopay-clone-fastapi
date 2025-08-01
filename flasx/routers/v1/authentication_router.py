from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasicCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)


from sqlmodel import select
from typing import Annotated
import datetime

from flasx.core import config
from flasx.core import security
from ... import models

router = APIRouter(tags=["authentication"])

settings = config.get_settings()


@router.post("/token")
async def authentication(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[models.AsyncSession, Depends(models.get_session)],
) -> models.Token:
    print("form_data", form_data)

    # Try to find user by citizen_id first
    result = await session.exec(
        select(models.DBUser).where(models.DBUser.citizen_id == form_data.username)
    )
    user = result.one_or_none()

    # If not found, try to find by phone_number
    if not user:
        result = await session.exec(
            select(models.DBUser).where(models.DBUser.phone_number == form_data.username)
        )
        user = result.one_or_none()

    print("user", user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect citizen ID/phone number or password",
        )

    if not await user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect citizen ID/phone number or password",
        )

    user.last_login_date = datetime.datetime.now()
    session.add(user)
    await session.commit()
    await session.refresh(user)

    access_token_expires = datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return models.Token(
        access_token=security.create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        refresh_token=security.create_refresh_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.datetime.now() + access_token_expires,
        issued_at=user.last_login_date,
        user_id=user.id,
    )