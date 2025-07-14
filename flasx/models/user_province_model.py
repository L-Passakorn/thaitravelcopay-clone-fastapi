import datetime
from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field


class BaseUserProvince(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    user_id: int
    province_id: int


class UserProvince(BaseUserProvince):
    id: int
    created_date: datetime.datetime


class UserProvinceList(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    user_provinces: list[UserProvince]


class AddUserProvince(BaseModel):
    province_id: int


class DBUserProvince(SQLModel, table=True):
    __tablename__ = "user_provinces"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    province_id: int = Field(foreign_key="provinces.id")
    created_date: datetime.datetime = Field(default_factory=datetime.datetime.now)


class UserProvinceQuota(BaseModel):
    """Model to show user's province quota status"""
    total_provinces: int
    primary_provinces: int
    secondary_provinces: int
    remaining_primary_quota: int
    remaining_secondary_quota: int
    max_primary_quota: int = 3
    max_secondary_quota: int = 2
    max_total_quota: int = 5
