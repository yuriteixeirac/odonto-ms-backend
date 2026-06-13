from typing import Any

from rest_framework.response import Response


def api_response(
    *,
    data: dict = {},
    message: str | None = "Operação realizada com sucesso.",
    success: bool = True,
    errors: Any = None,
    meta: dict = {},
    status: int = 200,
):
    return Response(
        {
            "success": success,
            "message": message,
            "data": data,
            "errors": errors,
            "meta": meta or {},
        },
        status=status,
    )
