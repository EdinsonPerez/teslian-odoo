from odoo import fields, models, _
from odoo.exceptions import UserError

from ..services.teslian_connect_client import (
    TeslianConnectClient,
    TeslianConnectError,
)


class ResPartner(models.Model):
    _inherit = "res.partner"

    redgps_client_id = fields.Char(
        string="ID Cliente RED GPS",
        index=True,
        help="Identificador del cliente dentro de RED GPS.",
    )

    teslian_asset_ids = fields.One2many(
        "teslian.asset",
        "partner_id",
        string="Activos",
    )

    teslian_billing_status = fields.Selection(
        [
            ("not_checked", "Pendiente de validación"),
            ("matched", "Validado"),
            ("review", "Requiere revisión"),
            ("error", "Error de integración"),
        ],
        string="Estado conciliación TESLIAN",
        default="not_checked",
        readonly=True,
        tracking=True,
    )

    teslian_can_invoice = fields.Boolean(
        string="Habilitado para facturar",
        default=False,
        readonly=True,
        tracking=True,
    )

    teslian_last_reconciliation = fields.Datetime(
        string="Última conciliación",
        readonly=True,
    )

    teslian_reconciliation_message = fields.Text(
        string="Resultado de conciliación",
        readonly=True,
    )

    teslian_missing_in_redgps = fields.Text(
        string="Faltantes en RED GPS",
        readonly=True,
    )

    teslian_missing_in_odoo = fields.Text(
        string="Faltantes en Odoo",
        readonly=True,
    )

    def action_teslian_reconcile(self):
        self.ensure_one()

        if not self.redgps_client_id:
            raise UserError(
                _(
                    "El cliente no posee un ID de RED GPS "
                    "configurado."
                )
            )

        operational_assets = self.teslian_asset_ids.filtered(
            lambda asset: asset.operational
        )

        payload = {
            "client": {
                "odoo_id": self.id,
                "external_id": self.redgps_client_id,
                "name": self.name,
                "active": self.active,
                "assets": [
                    {
                        "odoo_id": asset.id,
                        "external_id": asset.redgps_asset_id,
                        "name": asset.name,
                        "imei": asset.imei or None,
                        "plate": asset.plate or None,
                        "active": asset.operational,
                    }
                    for asset in operational_assets
                ],
            },
            "billing_period": fields.Date.today().strftime(
                "%Y-%m"
            ),
        }

        client = TeslianConnectClient.from_odoo_env(
            self.env
        )

        try:
            result = client.reconcile(
                payload
            )

        except TeslianConnectError as exc:
            self.write({
                "teslian_billing_status": "error",
                "teslian_can_invoice": False,
                "teslian_last_reconciliation": (
                    fields.Datetime.now()
                ),
                "teslian_reconciliation_message": str(exc),
            })

            raise UserError(
                _(
                    "No fue posible realizar la conciliación "
                    "contra TESLIAN CONNECT.\n\n%s"
                ) % exc
            )

        can_invoice = bool(
            result.get("can_invoice")
        )

        status = (
            "matched"
            if can_invoice
            else "review"
        )

        missing_in_redgps = result.get(
            "missing_in_redgps",
            [],
        )

        missing_in_odoo = result.get(
            "missing_in_odoo",
            [],
        )

        self.write({
            "teslian_billing_status": status,
            "teslian_can_invoice": can_invoice,
            "teslian_last_reconciliation": (
                fields.Datetime.now()
            ),
            "teslian_reconciliation_message": (
                result.get("message")
            ),
            "teslian_missing_in_redgps": (
                ", ".join(missing_in_redgps)
            ),
            "teslian_missing_in_odoo": (
                ", ".join(missing_in_odoo)
            ),
        })

        if not can_invoice:
            self.message_post(
                body=_(
                    "<b>ALERTA TESLIAN CONNECT</b><br/>"
                    "Se detectaron diferencias entre "
                    "Odoo y RED GPS.<br/><br/>"
                    "<b>Facturación bloqueada.</b><br/>"
                    "Se requiere revisión manual.<br/><br/>"
                    "<b>Activos Odoo:</b> %s<br/>"
                    "<b>Activos RED GPS:</b> %s<br/>"
                    "<b>Faltantes en RED GPS:</b> %s<br/>"
                    "<b>Faltantes en Odoo:</b> %s"
                ) % (
                    result.get("expected_assets"),
                    result.get("redgps_assets"),
                    missing_in_redgps or "-",
                    missing_in_odoo or "-",
                )
            )

        else:
            self.message_post(
                body=_(
                    "<b>TESLIAN CONNECT</b><br/>"
                    "Conciliación completada correctamente.<br/>"
                    "Cliente habilitado para facturación."
                )
            )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": (
                    _("Conciliación correcta")
                    if can_invoice
                    else _("Revisión requerida")
                ),
                "message": (
                    result.get("message")
                    or ""
                ),
                "type": (
                    "success"
                    if can_invoice
                    else "danger"
                ),
                "sticky": not can_invoice,
            },
        }