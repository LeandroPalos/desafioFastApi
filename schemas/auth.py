from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["leandro"])
    email: EmailStr = Field(..., examples=["leandro@example.com"])
    full_name: str = Field(..., min_length=1, max_length=120, examples=["Leandro Palos"])
    password: str = Field(..., min_length=6, max_length=128, examples=["senha123"])


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
