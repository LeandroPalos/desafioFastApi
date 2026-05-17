# Desafio FastAPI - API Bancária Assíncrona

API RESTful **assíncrona** para gerenciar contas correntes, depósitos e saques, com autenticação **JWT**.

## Stack

- **FastAPI** — framework web assíncrono
- **SQLAlchemy 2.0 (async)** + **aiosqlite** — ORM e driver async para SQLite
- **Pydantic v2** + **pydantic-settings** — schemas, validação e config via `.env`
- **python-jose** — emissão e verificação de JWT
- **bcrypt** — hash de senhas
- **Uvicorn** — servidor ASGI

## Funcionalidades

- Cadastro e autenticação de usuários (senha com hash bcrypt + token JWT)
- CRUD de contas correntes (uma conta pertence a um usuário)
- Transações: **depósito** e **saque** com validações de valor e saldo
- **Extrato** da conta com histórico completo de transações
- Mensagens de erro em **português** (incluindo erros de validação do Pydantic)
- Documentação **OpenAPI / Swagger** automática em `/docs`

## Pré-requisitos

- Python 3.11 ou superior (testado em 3.14)

## Instalação

```bash
# 1. Entrar na pasta do projeto
cd desafioFastApi

# 2. Criar e ativar um ambiente virtual
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
# Windows
copy .env.example .env
# Linux / macOS
cp .env.example .env

# Em seguida, abra o .env e troque SECRET_KEY por um valor seguro:
python -c "import secrets; print(secrets.token_hex(32))"
```

## Como rodar

Qualquer uma das opções abaixo sobe o servidor em `http://127.0.0.1:8000`:

```bash
# Opção 1 — pelo script (usa o bloco __main__ do entrypoint)
python desafioFastApi.py

# Opção 2 — via uvicorn diretamente (com auto-reload em mudanças)
uvicorn desafioFastApi:app --reload
```

O banco SQLite (`desafio.db`) é criado automaticamente no primeiro start.

## Como testar

A forma mais rápida é pelo **Swagger UI**:

1. Abra `http://127.0.0.1:8000/docs`
2. Em **`POST /auth/register`** → "Try it out" → criar um usuário
3. Em **`POST /auth/token`** → fazer login → copiar o `access_token`
4. Clicar no cadeado **Authorize** no topo → colar o token → Authorize
5. **`POST /accounts`** com `{"number": "0001-1"}` → criar a conta
6. **`POST /accounts/1/transactions`** com `{"type": "deposit", "amount": "500.00"}`
7. **`POST /accounts/1/transactions`** com `{"type": "withdraw", "amount": "150.00"}`
8. **`GET /accounts/1/extract`** → verifica saldo `350.00` e o histórico

## Endpoints

| Método | Rota                                      | Descrição                          | Auth |
|--------|-------------------------------------------|------------------------------------|------|
| GET    | `/`                                       | Health check                       | não  |
| POST   | `/auth/register`                          | Cadastra um novo usuário           | não  |
| POST   | `/auth/token`                             | Login (form-data); retorna o JWT   | não  |
| POST   | `/accounts`                               | Cria uma conta para o usuário      | sim  |
| GET    | `/accounts`                               | Lista as contas do usuário         | sim  |
| GET    | `/accounts/{id}`                          | Detalha uma conta                  | sim  |
| POST   | `/accounts/{id}/transactions`             | Depósito ou saque                  | sim  |
| GET    | `/accounts/{id}/extract`                  | Extrato (saldo + transações)       | sim  |

## Estrutura do projeto

```
desafioFastApi/
├── desafioFastApi.py       # entrypoint: cria o app, monta routers, registra handlers
├── config.py               # Settings via pydantic-settings (lê o .env)
├── database.py             # engine async, AsyncSession, Base, init_db
├── auth.py                 # hash bcrypt, JWT e dependência get_current_user
├── errors_pt.py            # handler global p/ traduzir erros do Pydantic para PT
├── models/                 # SQLAlchemy (User, Account, Transaction)
├── schemas/                # Pydantic (request/response)
├── routers/                # endpoints (auth, accounts, transactions)
├── requirements.txt
├── .env.example
└── .gitignore
```

## Modelagem de dados

```
User (1) ────< (N) Account (1) ────< (N) Transaction
```

- **User**: `id`, `username` (único), `email` (único), `full_name`, `hashed_password`
- **Account**: `id`, `number` (único), `balance` (Numeric 14,2), `owner_id` → User
- **Transaction**: `id`, `account_id` → Account, `type` (`deposit` | `withdraw`), `amount` (Numeric 14,2)

## Validações

- `amount` de depósito e saque deve ser **maior que zero** (Pydantic `gt=0`)
- Saque exige **saldo suficiente** — caso contrário, retorna **400 "Saldo insuficiente para saque"**
- Endpoints de conta/transação retornam **404** se a conta não pertencer ao usuário autenticado (isolamento por usuário)
- `username` e `email` são únicos — cadastro duplicado retorna **409**
- Acesso sem token retorna **401 "Não autenticado"**

## Variáveis de ambiente

| Variável                       | Padrão                                  | Descrição                          |
|--------------------------------|-----------------------------------------|------------------------------------|
| `DATABASE_URL`                 | `sqlite+aiosqlite:///./desafio.db`      | URL do banco (SQLAlchemy)          |
| `SECRET_KEY`                   | (defina no `.env`)                      | Chave para assinar o JWT           |
| `ALGORITHM`                    | `HS256`                                 | Algoritmo do JWT                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | `60`                                    | Tempo de vida do token, em minutos |
