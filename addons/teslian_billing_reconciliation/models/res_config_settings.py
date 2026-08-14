from odoo import _, fields, models
from odoo.exceptions import UserError

from ..services.teslian_connect_client import (
    TeslianConnectClient,
    TeslianConnectError,
)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    teslian_connect_base_url = fields.Char(
        string="TESLIAN CONNECT URL",
        config_parameter="teslian_connect.base_url",
        default="http://127.0.0.1:8000",
    )

    teslian_connect_api_key = fields.Char(
        string="TESLIAN CONNECT API Key",
        config_parameter="teslian_connect.api_key",
    )

    teslian_connect_timeout = fields.Integer(
        string="Timeout TESLIAN CONNECT",
        config_parameter="teslian_connect.timeout",
        default=120,
    )

    def action_test_teslian_connect(self):
        self.ensure_one()

        client = TeslianConnectClient(
            base_url=(
                self.teslian_connect_base_url
                or "http://127.0.0.1:8000"
            ),
            api_key=(
                self.teslian_connect_api_key
                or None
            ),
            timeout=(
                self.teslian_connect_timeout
                or 120
            ),
        )

        try:
            result = client.health()

        except TeslianConnectError as exc:
            raise UserError(
                _(
                    "No fue posible conectar con "
                    "TESLIAN CONNECT.\n\n%s"
                ) % exc
            )

        service = result.get(
            "service",
            "teslian-connect",
        )

        status = result.get(
            "status",
            "unknown",
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Conexión exitosa"),
                "message": _(
                    "TESLIAN CONNECT respondió correctamente. "
                    "Servicio: %s | Estado: %s"
                ) % (
                    service,
                    status,
                ),
                "type": "success",
                "sticky": False,
            },
        }