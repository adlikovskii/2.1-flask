import re
from pydantic import BaseModel, field_validator


class UserCreate(BaseModel):
    name: str
    email: str
    password: str

    @field_validator('name')
    @classmethod
    def check_name(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError('name must be at least 3 characters long')
        return v
    
    @field_validator('email')
    @classmethod
    def check_email(cls, v: str) -> str:
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(email_regex, v) is None:
            raise ValueError('invalid email address')
        return v
    
    @field_validator('password')
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('password must be at least 8 characters long')
        return v

class BaseAds(BaseModel):
    title: str
    description: str

    @field_validator('title')
    @classmethod
    def check_title(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError('title must be at least 3 characters long')
        return v
    
    @field_validator('description')
    @classmethod
    def check_description(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError('description must be at least 10 characters long')
        return v

class AdsCreate(BaseAds):
    pass

class UpdateAds(BaseAds):
    title: str | None
    description: str | None
