{
    "name": "TESLIAN Billing Reconciliation",
    "version": "19.0.1.0.0",
    "summary": (
        "Conciliación de clientes y activos "
        "entre Odoo, TESLIAN CONNECT y RED GPS"
    ),
    "description": """
TESLIAN Billing Reconciliation

Permite validar clientes y activos registrados en Odoo
contra la información disponible en RED GPS a través
de TESLIAN CONNECT antes de habilitar la facturación.
    """,
    "author": "TESLIAN GROUP",
    "website": "",
    "category": "Accounting",
    "license": "LGPL-3",

    "depends": [
        "base",
        "contacts",
        "mail",
        "account",
    ],

    "data": [
        # Se incorporarán en los siguientes pasos:
        # "security/ir.model.access.csv",
        # "views/teslian_asset_views.xml",
        # "views/res_partner_views.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False,
}