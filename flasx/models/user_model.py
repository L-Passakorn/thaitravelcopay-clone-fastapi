import datetime

import pydantic
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlmodel import SQLModel, Field

# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
import bcrypt


class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    email: str = pydantic.Field(json_schema_extra=dict(example="admin@email.local"))
    citizen_id: str = pydantic.Field(json_schema_extra=dict(example="1234567890123"))
    first_name: str = pydantic.Field(json_schema_extra=dict(example="John"))
    last_name: str = pydantic.Field(json_schema_extra=dict(example="Doe"))
    phone_number: str = pydantic.Field(json_schema_extra=dict(example="0801234567"))
    current_address: str = pydantic.Field(json_schema_extra=dict(example="Bangkok"))


class User(BaseUser):
    id: int
    last_login_date: datetime.datetime | None = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )
    register_date: datetime.datetime | None = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )


class ReferenceUser(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    username: str
    first_name: str
    last_name: str


class UserList(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    users: list[User]


class Login(BaseModel):
    email: EmailStr
    password: str


class ChangedPassword(BaseModel):
    current_password: str
    new_password: str


class ResetedPassword(BaseModel):
    email: EmailStr
    citizen_id: str


class RegisteredUser(BaseUser):
    password: str = pydantic.Field(json_schema_extra=dict(example="password"))


class UpdatedUser(BaseUser):
    pass  # Remove roles field since it's not defined in BaseUser


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    expires_at: datetime.datetime
    scope: str
    issued_at: datetime.datetime
    user_id: int


class ChangedPasswordUser(BaseModel):
    current_password: str
    new_password: str


class DBUser(BaseUser, SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    password: str
    phone_number: str
    current_address: str

    register_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    last_login_date: datetime.datetime | None = Field(default=None)

    async def get_encrypted_password(self, plain_password):
        return bcrypt.hashpw(
            plain_password.encode("utf-8"), salt=bcrypt.gensalt()
        ).decode("utf-8")

    async def set_password(self, plain_password):
        self.password = await self.get_encrypted_password(plain_password)

    async def verify_password(self, plain_password):
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), self.password.encode("utf-8")
        )
