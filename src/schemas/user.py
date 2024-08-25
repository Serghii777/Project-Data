import string
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator, model_validator, root_validator
from pydantic.v1 import validator


class UserReadSchema(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserDbSchema(UserReadSchema):
    role: str
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    confirmed: bool
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
    phone: Optional[int] = None
    vehicles: Optional[List["VehicleReadSchema"]] = None
    parking_records: Optional[List["ParkingRecordReadSchema"]] = None
    black_list: Optional[List["BlackListReadSchema"]] = None
    parking_duration: Optional[int] = None
    parking_history: Optional[List["ParkingHistorySchema"]] = None
    parking_last_entry: Optional[datetime] = None
    parking_last_exit: Optional[datetime] = None
    parking_cost: Optional[int] = None


class UserResponseSchema(BaseModel):
    user: UserDbSchema
    detail: str = "User successfully created."


class UserCreateSchema(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=12)
    password_confirmation: str = Field(..., min_length=8, max_length=12)
    phone: Optional[int] = None


class UserUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(min_length=2, max_length=50)
    last_name: Optional[str] = Field(min_length=2, max_length=50)
    email: Optional[EmailStr]


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class ConfirmationResponse(BaseModel):
    message: str


class LogoutResponseSchema(BaseModel):
    message: str


class RequestNewPassword(BaseModel):
    new_password: str = Field(min_length=8, max_length=12)
    

class VehicleReadSchema(BaseModel):
    id: uuid.UUID
    license_plate: str
    model: str
    color: str

    class Config:
        orm_mode = True


class ParkingRecordReadSchema(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    entry_time: datetime
    exit_time: Optional[datetime] = None
    duration: Optional[int] = None
    cost: Optional[int] = None

    class Config:
        orm_mode = True


class BlackListReadSchema(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    reason: str

    class Config:
        orm_mode = True


class ParkingHistorySchema(BaseModel):
    license_plate: str  
    entry_time: datetime
    exit_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None  
    cost: Optional[int] = None  

    class Config:
        orm_mode = True