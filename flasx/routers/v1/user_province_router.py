from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from typing import Annotated

from flasx.core import deps
from flasx import models

router = APIRouter(prefix="/user-provinces", tags=["user-provinces"])


@router.get("/my-quota")
async def get_my_quota(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.UserProvinceQuota:
    """Get current user's province quota status"""
    # Get user's provinces with tax rates
    result = await session.exec(
        select(models.DBProvince)
        .join(models.DBUserProvince)
        .where(models.DBUserProvince.user_id == current_user.id)
    )
    provinces = result.all()
    
    primary_count = sum(1 for p in provinces if p.tax_reduction_rate == 0.50)
    secondary_count = sum(1 for p in provinces if p.tax_reduction_rate == 0.25)
    
    return models.UserProvinceQuota(
        total_provinces=len(provinces),
        primary_provinces=primary_count,
        secondary_provinces=secondary_count,
        remaining_primary_quota=max(0, 3 - primary_count),
        remaining_secondary_quota=max(0, 2 - secondary_count),
    )


@router.get("/my-provinces")
async def get_my_provinces(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> list[models.Province]:
    """Get all provinces assigned to current user"""
    result = await session.exec(
        select(models.DBProvince)
        .join(models.DBUserProvince)
        .where(models.DBUserProvince.user_id == current_user.id)
    )
    provinces = result.all()
    return provinces


@router.post("/target-province")
async def add_target_province(
    province_data: models.AddUserProvince,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:
    """Add a target province to current user with quota validation"""
    
    # Check if province exists
    province = await session.get(models.DBProvince, province_data.province_id)
    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found",
        )
    
    # Check if province matches user's current address
    user_address_lower = current_user.current_address.lower()
    province_name_lower = province.name.lower()
    
    # Check if province name is contained in user's address or vice versa
    if (province_name_lower in user_address_lower or 
        user_address_lower in province_name_lower or
        province_name_lower == user_address_lower):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot select province '{province.name}' as it matches your registered address '{current_user.current_address}'",
        )
    
    # Check if user already has this province
    result = await session.exec(
        select(models.DBUserProvince).where(
            models.DBUserProvince.user_id == current_user.id,
            models.DBUserProvince.province_id == province_data.province_id
        )
    )
    existing = result.one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Province '{province.name}' is already your target province",
        )
    
    # Get current quota status
    quota = await get_my_quota(session, current_user)
    
    # Check total quota
    if quota.total_provinces >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum total quota of 5 target provinces reached",
        )
    
    # Check specific quota based on province type
    is_primary = province.tax_reduction_rate == 0.50
    
    if is_primary and quota.remaining_primary_quota <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum primary province quota of 3 reached",
        )
    
    if not is_primary and quota.remaining_secondary_quota <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum secondary province quota of 2 reached",
        )
    
    # Add province to user
    user_province = models.DBUserProvince(
        user_id=current_user.id,
        province_id=province_data.province_id
    )
    session.add(user_province)
    await session.commit()
    
    province_type = "primary" if is_primary else "secondary"
    return {
        "message": f"Successfully added {province_type} province '{province.name}' as target province",
        "province_id": province.id,
        "province_name": province.name,
        "province_type": province_type,
        "tax_reduction_rate": province.tax_reduction_rate,
        "remaining_quota": {
            "primary": quota.remaining_primary_quota - (1 if is_primary else 0),
            "secondary": quota.remaining_secondary_quota - (1 if not is_primary else 0),
            "total": quota.total_provinces + 1
        }
    }


@router.delete("/target-province/{province_id}")
async def remove_target_province(
    province_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:
    """Remove a target province from current user"""
    
    # Find user-province relationship
    result = await session.exec(
        select(models.DBUserProvince).where(
            models.DBUserProvince.user_id == current_user.id,
            models.DBUserProvince.province_id == province_id
        )
    )
    user_province = result.one_or_none()
    
    if not user_province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province is not in your target provinces list",
        )
    
    # Get province info for response
    province = await session.get(models.DBProvince, province_id)
    province_name = province.name if province else "Unknown"
    province_type = "primary" if province and province.tax_reduction_rate == 0.50 else "secondary"
    
    await session.delete(user_province)
    await session.commit()
    
    return {
        "message": f"Successfully removed {province_type} province '{province_name}' from target provinces",
        "province_id": province_id,
        "province_name": province_name,
        "province_type": province_type
    }


@router.get("/available-provinces")
async def get_available_provinces(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:
    """Get provinces available for user to add based on quota"""
    
    # Get current quota
    quota = await get_my_quota(session, current_user)
    
    # Get all provinces
    all_provinces_result = await session.exec(select(models.DBProvince))
    all_provinces = all_provinces_result.all()
    
    # Get user's current provinces
    user_provinces_result = await session.exec(
        select(models.DBUserProvince.province_id).where(
            models.DBUserProvince.user_id == current_user.id
        )
    )
    user_province_ids = [up for up in user_provinces_result.all()]
    
    # Filter available provinces
    available_primary = []
    available_secondary = []
    excluded_provinces = []
    
    user_address_lower = current_user.current_address.lower()
    
    for province in all_provinces:
        # Skip if user already has this province
        if province.id in user_province_ids:
            continue
            
        # Skip if province matches user's address
        province_name_lower = province.name.lower()
        if (province_name_lower in user_address_lower or 
            user_address_lower in province_name_lower or
            province_name_lower == user_address_lower):
            excluded_provinces.append({
                "id": province.id,
                "name": province.name,
                "reason": "matches_user_address"
            })
            continue
            
        if province.tax_reduction_rate == 0.50 and quota.remaining_primary_quota > 0:
            available_primary.append(province)
        elif province.tax_reduction_rate == 0.25 and quota.remaining_secondary_quota > 0:
            available_secondary.append(province)
    
    return {
        "quota_status": quota,
        "user_address": current_user.current_address,
        "available_provinces": {
            "primary": available_primary,
            "secondary": available_secondary
        },
        "excluded_provinces": excluded_provinces,
        "total_available": len(available_primary) + len(available_secondary),
        "total_excluded": len(excluded_provinces)
    }


@router.get("/{user_id}/provinces")
async def get_user_provinces(
    user_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:
    """Get provinces assigned to a specific user (admin function)"""
    
    # Check if target user exists
    target_user = await session.get(models.DBUser, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Get user's provinces
    result = await session.exec(
        select(models.DBProvince)
        .join(models.DBUserProvince)
        .where(models.DBUserProvince.user_id == user_id)
    )
    provinces = result.all()
    
    primary_provinces = [p for p in provinces if p.tax_reduction_rate == 0.50]
    secondary_provinces = [p for p in provinces if p.tax_reduction_rate == 0.25]
    
    return {
        "user_id": user_id,
        "user_name": f"{target_user.first_name} {target_user.last_name}",
        "total_provinces": len(provinces),
        "primary_provinces": primary_provinces,
        "secondary_provinces": secondary_provinces,
        "quota_usage": {
            "primary_used": len(primary_provinces),
            "primary_remaining": max(0, 3 - len(primary_provinces)),
            "secondary_used": len(secondary_provinces),
            "secondary_remaining": max(0, 2 - len(secondary_provinces)),
            "total_used": len(provinces),
            "total_remaining": max(0, 5 - len(provinces))
        }
    }
    """Get provinces assigned to a specific user (admin function)"""
    
    # Check if target user exists
    target_user = await session.get(models.DBUser, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Get user's provinces
    result = await session.exec(
        select(models.DBProvince)
        .join(models.DBUserProvince)
        .where(models.DBUserProvince.user_id == user_id)
    )
    provinces = result.all()
    
    primary_provinces = [p for p in provinces if p.tax_reduction_rate == 0.50]
    secondary_provinces = [p for p in provinces if p.tax_reduction_rate == 0.25]
    
    return {
        "user_id": user_id,
        "user_name": f"{target_user.first_name} {target_user.last_name}",
        "total_provinces": len(provinces),
        "primary_provinces": primary_provinces,
        "secondary_provinces": secondary_provinces,
        "quota_usage": {
            "primary_used": len(primary_provinces),
            "primary_remaining": max(0, 3 - len(primary_provinces)),
            "secondary_used": len(secondary_provinces),
            "secondary_remaining": max(0, 2 - len(secondary_provinces)),
            "total_used": len(provinces),
            "total_remaining": max(0, 5 - len(provinces))
        }
    }
