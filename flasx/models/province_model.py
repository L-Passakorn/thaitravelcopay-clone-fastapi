import datetime
import pydantic
from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field


class BaseProvince(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    name: str = pydantic.Field(json_schema_extra=dict(example="Bangkok"))
    tax_reduction_rate: float = pydantic.Field(json_schema_extra=dict(example=0.50))


class Province(BaseProvince):
    id: int


class ProvinceList(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    provinces: list[Province]


class RegisteredProvince(BaseProvince):
    pass


class UpdatedProvince(BaseProvince):
    pass


class DBProvince(BaseProvince, SQLModel, table=True):
    __tablename__ = "provinces"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    tax_reduction_rate: float
    
    created_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
