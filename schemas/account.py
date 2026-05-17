from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    number: str = Field(..., min_length=1, max_length=20, examples=["0001-1"])


class AccountResponse(BaseModel):
    id: int
    number: str
    balance: Decimal
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
