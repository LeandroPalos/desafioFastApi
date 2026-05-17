from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models import Account, User
from schemas.account import AccountCreate, AccountResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova conta corrente para o usuário autenticado",
)
async def create_account(
    payload: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Account:
    existing = await db.execute(select(Account).where(Account.number == payload.number))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Número de conta já existe",
        )

    account = Account(number=payload.number, owner_id=current_user.id)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get(
    "",
    response_model=list[AccountResponse],
    summary="Lista as contas do usuário autenticado",
)
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Account]:
    result = await db.execute(select(Account).where(Account.owner_id == current_user.id))
    return list(result.scalars().all())


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Detalha uma conta do usuário autenticado",
)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Account:
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if account is None or account.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conta não encontrada")
    return account
