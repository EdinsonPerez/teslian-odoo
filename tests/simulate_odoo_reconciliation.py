from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SERVICE_DIR = (
    PROJECT_ROOT
    / "addons"
    / "teslian_billing_reconciliation"
    / "services"
)

if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))


from teslian_connect_client import (  # noqa: E402
    TeslianConnectClient,
    TeslianConnectError,
)


TESLIAN_CONNECT_URL = "http://127.0.0.1:8000"


def main() -> None:
    print("=" * 70)
    print("TESLIAN ODOO - Simulación de conciliación")
    print("=" * 70)

    payload = {
        "client": {
            "odoo_id": 157,
            "external_id": "39348",
            "name": "Cliente Demo",
            "active": True,
            "assets": [
                {
                    "odoo_id": 1,
                    "external_id": "158063",
                    "name": "Activo 1",
                    "imei": None,
                    "plate": None,
                    "active": True,
                },
                {
                    "odoo_id": 2,
                    "external_id": "158121",
                    "name": "Activo 2",
                    "imei": None,
                    "plate": None,
                    "active": True,
                },
                {
                    "odoo_id": 3,
                    "external_id": "158167",
                    "name": "Activo 3",
                    "imei": None,
                    "plate": None,
                    "active": True,
                },
                {
                    "odoo_id": 4,
                    "external_id": "158198",
                    "name": "Activo 4",
                    "imei": None,
                    "plate": None,
                    "active": True,
                },
                {
                    "odoo_id": 5,
                    "external_id": "158223",
                    "name": "Activo 5",
                    "imei": None,
                    "plate": None,
                    "active": True,
                },
                {
                    "odoo_id": 6,
                    "external_id": "158230",
                    "name": "Activo 6",
                    "imei": None,
                    "plate": None,
                    "active": True,
                },
                {
                    "odoo_id": 7,
                    "external_id": "158251",
                    "name": "Activo 7",
                    "imei": None,
                    "plate": None,
                    "active": True,
                },
                {
                    "odoo_id": 8,
                    "external_id": "158400",
                    "name": "Activo 8",
                    "imei": None,
                    "plate": None,
                    "active": True,
                },

                {
                    "odoo_id": 9,
                    "external_id": "266797",
                    "name": "Activo 9",
                    "imei": None,
                    "plate": None,
                    "active": True,
                },

                
            ],
        },
        "billing_period": "2026-08",
    }

    client = TeslianConnectClient(
        TESLIAN_CONNECT_URL
    )

    try:
        result = client.reconcile(payload)

    except TeslianConnectError as exc:
        print("\nERROR")
        print(exc)
        return

    print("\nResultado recibido desde TESLIAN CONNECT")
    print("-" * 70)

    print("Status:", result.get("status"))
    print(
        "Puede facturar:",
        result.get("can_invoice"),
    )
    print(
        "Cliente coincide:",
        result.get("client_match"),
    )
    print(
        "Activos coinciden:",
        result.get("assets_match"),
    )
    print(
        "Activos Odoo:",
        result.get("expected_assets"),
    )
    print(
        "Activos RED GPS:",
        result.get("redgps_assets"),
    )
    print(
        "Faltantes RED GPS:",
        result.get("missing_in_redgps"),
    )
    print(
        "Faltantes Odoo:",
        result.get("missing_in_odoo"),
    )
    print(
        "Mensaje:",
        result.get("message"),
    )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()