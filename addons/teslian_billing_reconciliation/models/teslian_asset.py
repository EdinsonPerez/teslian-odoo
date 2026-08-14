from odoo import fields, models


class TeslianAsset(models.Model):
    _name = "teslian.asset"
    _description = "Activo TESLIAN"
    _order = "name"

    name = fields.Char(
        string="Activo",
        required=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Cliente",
        required=True,
        ondelete="cascade",
        index=True,
    )

    redgps_asset_id = fields.Char(
        string="ID Activo RED GPS",
        required=True,
        index=True,
        help="Identificador del activo en RED GPS.",
    )

    imei = fields.Char(
        string="IMEI",
        help="IMEI del dispositivo GPS asociado al activo.",
    )

    plate = fields.Char(
        string="Identificación / Placa",
    )

    operational = fields.Boolean(
        string="Activo operativo",
        default=True,
        help=(
            "Indica si este activo debe participar "
            "en la conciliación de facturación."
        ),
    )

    last_reconciliation_status = fields.Selection(
        [
            ("not_checked", "Pendiente"),
            ("matched", "Coincide"),
            ("review", "Requiere revisión"),
        ],
        string="Estado de conciliación",
        default="not_checked",
        readonly=True,
    )

    last_reconciliation_date = fields.Datetime(
        string="Última conciliación",
        readonly=True,
    )