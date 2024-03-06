from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
# from pydantic_extra_types.phone_numbers import PhoneNumber 


class ContactModel(BaseModel):
    first_name: str = Field(max_length=50,  description="First name")
    last_name:  str = Field(max_length=50,  description="Last name")
    email:      EmailStr 
    # phone:      PhoneNumber = Field(min_length=10, max_length = 15, phone_format=)
    phone:      str = Field(min_length=10, max_length = 15)
    birthday:   date
    notes:      Optional[str] = Field(default=None, description="Contact notes")


class ContactResponse(ContactModel):
    id:         int
    first_name: str
    last_name:  str
    email:      str
    phone:      str
    birthday:   date 
    notes:      str

    class Config:
        from_attributes = True


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email:    EmailStr
    password: str = Field(min_length=6, max_length=20)


class UserDb(BaseModel):
    id:         int
    username:   str
    email:      str
    created_at: datetime
    avatar:     str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user:   UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token:   str
    refresh_token:  str
    token_type:     str = "bearer"


class EmailSchema(BaseModel):
    email: EmailStr

class RequestEmail(BaseModel):
    email: EmailStr
    