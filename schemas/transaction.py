from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.transaction import TransactionType


class TransactionCreate(BaseModel):
    type: TransactionType = Field(..., description="Tipo da transação: 'deposit' (depósito) ou 'withdraw' (saque)")
    amount: Decimal = Field(..., gt=0, max_digits=14, decimal_places=2, examples=["100.50"])


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    type: TransactionType
    amount: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExtractResponse(BaseModel):
    account_id: int
    account_number: str
    balance: Decimal
    transactions: list[TransactionResponse]
