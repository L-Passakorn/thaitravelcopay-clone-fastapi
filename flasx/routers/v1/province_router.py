from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from typing import Annotated

from flasx.core import deps
from flasx import models

router = APIRouter(prefix="/provinces", tags=["provinces"])


@router.get("/")
async def get_all(
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.ProvinceList:
    result = await session.exec(select(models.DBProvince))
    provinces = result.all()
    return models.ProvinceList(provinces=provinces)


@router.get("/{province_id}")
async def get(
    province_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Province:
    province = await session.get(models.DBProvince, province_id)
    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found",
        )
    return province


@router.get("/name/{province_name}")
async def get_by_name(
    province_name: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Province:
    result = await session.exec(
        select(models.DBProvince).where(models.DBProvince.name == province_name)
    )
    province = result.one_or_none()

    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found",
        )
    return province


@router.get("/primary/")
async def get_primary_provinces(
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.ProvinceList:
    result = await session.exec(
        select(models.DBProvince).where(models.DBProvince.tax_reduction_rate == 0.50)
    )
    provinces = result.all()
    return models.ProvinceList(provinces=provinces)


@router.get("/secondary/")
async def get_secondary_provinces(
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.ProvinceList:
    result = await session.exec(
        select(models.DBProvince).where(models.DBProvince.tax_reduction_rate == 0.25)
    )
    provinces = result.all()
    return models.ProvinceList(provinces=provinces)


@router.put("/{province_id}")
async def update(
    province_id: int,
    province_update: models.UpdatedProvince,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.Province:
    province = await session.get(models.DBProvince, province_id)

    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found",
        )

    # Check if new name conflicts with existing province (if name is being changed)
    if province_update.name != province.name:
        result = await session.exec(
            select(models.DBProvince).where(
                models.DBProvince.name == province_update.name
            )
        )
        existing_province = result.one_or_none()

        if existing_province:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Province name already exists",
            )

    # Update province fields
    for field, value in province_update.model_dump(exclude_unset=True).items():
        setattr(province, field, value)

    province.updated_date = models.datetime.datetime.now()
    session.add(province)
    await session.commit()
    await session.refresh(province)

    return province


@router.delete("/{province_id}")
async def delete(
    province_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:
    province = await session.get(models.DBProvince, province_id)

    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found",
        )

    await session.delete(province)
    await session.commit()

    return {"message": "Province deleted successfully"}
