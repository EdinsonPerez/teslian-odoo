from __future__ import annotations

from typing import Any

import requests


class TeslianConnectError(RuntimeError):
    """Error controlado al comunicarse con TESLIAN CONNECT."""


class TeslianConnectClient:
    """
    Cliente HTTP para consumir TESLIAN CONNECT.

    Puede utilizarse:
    - desde pruebas independientes;
    - desde el runtime de Odoo mediante from_odoo_env().
    """

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str | None = None,
        timeout: int | float = 120,
    ) -> None:
        if not base_url.strip():
            raise ValueError(
                "base_url no puede estar vacío."
            )

        if timeout <= 0:
            raise ValueError(
                "timeout debe ser mayor que cero."
            )

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    @classmethod
    def from_odoo_env(
        cls,
        env,
    ) -> "TeslianConnectClient":
        """
        Construye el cliente utilizando parámetros
        configurados dentro de Odoo.
        """

        config = env[
            "ir.config_parameter"
        ].sudo()

        base_url = config.get_param(
            "teslian_connect.base_url",
            "http://127.0.0.1:8000",
        )

        api_key = config.get_param(
            "teslian_connect.api_key",
            "",
        )

        timeout_raw = config.get_param(
            "teslian_connect.timeout",
            "120",
        )

        try:
            timeout = int(timeout_raw)

        except (TypeError, ValueError):
            timeout = 120

        return cls(
            base_url=base_url,
            api_key=api_key or None,
            timeout=timeout,
        )

    def _build_headers(self) -> dict[str, str]:
        """
        Construye headers comunes para TESLIAN CONNECT.
        """

        headers = {
            "Accept": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = (
                f"Bearer {self.api_key}"
            )

        return headers

    def health(self) -> dict[str, Any]:
        """
        Verifica disponibilidad de TESLIAN CONNECT.
        """

        url = (
            f"{self.base_url}/health"
        )

        try:
            response = requests.get(
                url,
                headers=self._build_headers(),
                timeout=min(
                    self.timeout,
                    30,
                ),
            )

        except requests.RequestException as exc:
            raise TeslianConnectError(
                "No fue posible conectar con "
                f"TESLIAN CONNECT: {exc}"
            ) from exc

        if not response.ok:
            raise TeslianConnectError(
                "TESLIAN CONNECT respondió con error. "
                f"HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )

        try:
            result = response.json()

        except ValueError as exc:
            raise TeslianConnectError(
                "TESLIAN CONNECT respondió con "
                "contenido no JSON."
            ) from exc

        if not isinstance(
            result,
            dict,
        ):
            raise TeslianConnectError(
                "TESLIAN CONNECT devolvió "
                "una respuesta inesperada."
            )

        return result

    def reconcile(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ejecuta la conciliación de facturación
        contra TESLIAN CONNECT.
        """

        url = (
            f"{self.base_url}"
            "/api/v1/billing/reconcile"
        )

        headers = self._build_headers()

        headers[
            "Content-Type"
        ] = "application/json"

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )

        except requests.RequestException as exc:
            raise TeslianConnectError(
                "No fue posible conectar con "
                f"TESLIAN CONNECT: {exc}"
            ) from exc

        if not response.ok:
            raise TeslianConnectError(
                "TESLIAN CONNECT respondió con error. "
                f"HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )

        try:
            result = response.json()

        except ValueError as exc:
            raise TeslianConnectError(
                "TESLIAN CONNECT respondió con "
                "contenido que no es JSON válido."
            ) from exc

        if not isinstance(
            result,
            dict,
        ):
            raise TeslianConnectError(
                "TESLIAN CONNECT devolvió "
                "una respuesta inesperada."
            )

        required_fields = {
            "status",
            "can_invoice",
            "client_match",
            "assets_match",
            "expected_assets",
            "redgps_assets",
        }

        missing_fields = (
            required_fields
            - result.keys()
        )

        if missing_fields:
            raise TeslianConnectError(
                "La respuesta de TESLIAN CONNECT "
                "no contiene todos los campos requeridos. "
                f"Faltantes: {sorted(missing_fields)}"
            )

        return result