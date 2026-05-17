from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models import Account, Transaction, TransactionType, User
from schemas.transaction import ExtractResponse, TransactionCreate, TransactionResponse

router = APIRouter(prefix="/accounts/{account_id}", tags=["transactions"])


async def _get_owned_account(account_id: int, user: User, db: AsyncSession) -> Account:
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if account is None or account.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada")
    return account


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Realiza um depósito ou saque na conta",
)
async def create_transaction(
    account_id: int,
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Transaction:
    account = await _get_owned_account(account_id, current_user, db)
    amount = Decimal(payload.amount)

    if payload.type == TransactionType.WITHDRAW:
        if account.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Saldo insuficiente para saque",
            )
        account.balance = account.balance - amount
    else:
        account.balance = account.balance + amount

    tx = Transaction(account_id=account.id, type=payload.type, amount=amount)
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


@router.get(
    "/extract",
    response_model=ExtractResponse,
    summary="Retorna o extrato da conta com todas as transações",
)
async def get_extract(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExtractResponse:
    account = await _get_owned_account(account_id, current_user, db)
    result = await db.execute(
        select(Transaction)
        .where(Transaction.account_id == account.id)
        .order_by(Transaction.created_at.desc())
    )
    transactions = list(result.scalars().all())
    return ExtractResponse(
        account_id=account.id,
        account_number=account.number,
        balance=account.balance,
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
    )
