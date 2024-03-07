from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
# from pydantic_extra_types.phone_numbers import PhoneNumber 


class ContactModel(BaseModel):
    """
    Contact Model schema for pydantic validation

    Args:
        BaseModel: Inherited from BaseModel
    """
    first_name: str = Field(max_length=50,  description="First name")
    last_name:  str = Field(max_length=50,  description="Last name")
    email:      EmailStr 
    # phone:      PhoneNumber = Field(min_length=10, max_length = 15, phone_format=)
    phone:      str = Field(min_length=10, max_length = 15)
    birthday:   date
    notes:      Optional[str] = Field(default=None, description="Contact notes")


class ContactResponse(ContactModel):
    """
    Contact Response schema for pydantic validation

    Args:
        ContactModel: Inherited from ContactModel
    """
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
    """
    User Model schema for pydantic validation

    Args:
        BaseModel: Inherited from BaseModel
    """
    username: str = Field(min_length=5, max_length=16)
    email:    EmailStr
    password: str = Field(min_length=6, max_length=20)


class UserDb(BaseModel):
    """
    User DB object schema for pydantic validation

    Args:
        BaseModel: Inherited from BaseModel
    """
    id:         int
    username:   str
    email:      str
    created_at: datetime
    avatar:     str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    User Responce schema for pydantic validation

    Args:
        BaseModel: Inherited from BaseModel
    """
    user:   UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    Token model schema for pydantic validation

    Args:
        BaseModel: Inherited from BaseModel
    """
    access_token:   str
    refresh_token:  str
    token_type:     str = "bearer"


class RequestEmail(BaseModel):
    """
    Email schema for pydantic validation

    Args:
        BaseModel: Inherited from BaseModel
    """
    email: EmailStr
    