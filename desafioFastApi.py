from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from database import init_db
from errors_pt import validation_exception_handler
from routers import accounts, auth, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Desafio FastAPI - API Bancária Assíncrona",
    description="API RESTful assíncrona para gerenciar contas correntes, depósitos e saques, com autenticação JWT.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)


@app.get("/", tags=["health"], summary="Verificação de saúde")
async def root() -> dict[str, str]:
    return {"status": "ok", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("desafioFastApi:app", host="127.0.0.1", port=8000, reload=True)
