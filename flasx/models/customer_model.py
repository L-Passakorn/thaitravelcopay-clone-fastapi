from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .parcel_model import Parcel


class CustomerBase(SQLModel):
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    phone: str | None = None
    address: Optional[str] = None
    is_active: bool = Field(default=True)


class Customer(CustomerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    sent_parcels: list["Parcel"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "Parcel.sender_id"},
    )
    received_parcels: list["Parcel"] = Relationship(
        back_populates="receiver",
        sa_relationship_kwargs={"foreign_keys": "Parcel.receiver_id"},
    )
