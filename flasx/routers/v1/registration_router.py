from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Annotated

from flasx import models

router = APIRouter(tags=["registration"])


@router.post("/register")
async def register_user(
    user_info: models.RegisteredUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.User:
    # Check if citizen_id already exists
    result = await session.exec(
        select(models.DBUser).where(models.DBUser.citizen_id == user_info.citizen_id)
    )
    existing_user = result.one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Citizen ID already exists"
        )

    # Check if phone_number already exists
    result = await session.exec(
        select(models.DBUser).where(
            models.DBUser.phone_number == user_info.phone_number
        )
    )
    existing_phone = result.one_or_none()

    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Phone number already exists"
        )

    # Check if email already exists
    result = await session.exec(
        select(models.DBUser).where(models.DBUser.email == user_info.email)
    )
    existing_email = result.one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )

    # Create new user
    new_user = models.DBUser(
        citizen_id=user_info.citizen_id,
        email=user_info.email,
        first_name=user_info.first_name,
        last_name=user_info.last_name,
        phone_number=user_info.phone_number,
        current_address=user_info.current_address,
        password="",  # Will be set below
    )

    await new_user.set_password(user_info.password)

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return models.User(
        id=new_user.id,
        citizen_id=new_user.citizen_id,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        phone_number=new_user.phone_number,
        current_address=new_user.current_address,
        register_date=new_user.register_date,
        last_login_date=new_user.last_login_date,
    )
