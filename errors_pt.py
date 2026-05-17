from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


_MENSAGENS = {
    "missing": "Campo obrigatório",
    "string_too_short": "Texto deve ter no mínimo {min_length} caracteres",
    "string_too_long": "Texto deve ter no máximo {max_length} caracteres",
    "string_type": "Valor deve ser um texto",
    "int_type": "Valor deve ser um número inteiro",
    "float_type": "Valor deve ser um número",
    "decimal_type": "Valor deve ser um número decimal",
    "bool_type": "Valor deve ser verdadeiro ou falso",
    "greater_than": "Valor deve ser maior que {gt}",
    "greater_than_equal": "Valor deve ser maior ou igual a {ge}",
    "less_than": "Valor deve ser menor que {lt}",
    "less_than_equal": "Valor deve ser menor ou igual a {le}",
    "decimal_max_digits": "Número excede o limite de dígitos permitido",
    "decimal_max_places": "Número de casas decimais excede o limite",
    "decimal_parsing": "Valor decimal inválido",
    "value_error": "Valor inválido",
    "enum": "Valor não permitido. Valores aceitos: {expected}",
    "literal_error": "Valor não permitido. Valores aceitos: {expected}",
    "json_invalid": "JSON inválido",
    "model_attributes_type": "Formato inválido",
    "extra_forbidden": "Campo não permitido",
}


def _traduzir(err: dict) -> str:
    template = _MENSAGENS.get(err["type"])
    if template is None:
        return err.get("msg", "Valor inválido")
    ctx = err.get("ctx") or {}
    try:
        return template.format(**ctx)
    except (KeyError, IndexError):
        return template


async def validation_exception_handler(_: Request, exc: RequestValidationError):
    erros = []
    for err in exc.errors():
        campo = ".".join(str(p) for p in err.get("loc", []) if p != "body")
        erros.append({"campo": campo or "(corpo)", "mensagem": _traduzir(err)})
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": erros})
