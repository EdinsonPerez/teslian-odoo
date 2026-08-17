# pyright: reportMissingImports=false
from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    teslian_reconciliation_status = fields.Selection(
        [
            ("matched", "Validado"),
            ("review", "Requiere revisión"),
            ("not_checked", "Pendiente"),
            ("error", "Error de integración"),
        ],
        string="Conciliación TESLIAN utilizada",
        readonly=True,
        copy=False,
    )

    teslian_reconciliation_date = fields.Datetime(
        string="Fecha de conciliación TESLIAN",
        readonly=True,
        copy=False,
    )

    teslian_redgps_client_id = fields.Char(
        string="ID Cliente RED GPS",
        readonly=True,
        copy=False,
    )

    teslian_odoo_asset_count = fields.Integer(
        string="Activos Odoo validados",
        readonly=True,
        copy=False,
    )

    teslian_redgps_asset_count = fields.Integer(
        string="Activos RED GPS validados",
        readonly=True,
        copy=False,
    )

    teslian_reconciliation_message = fields.Text(
        string="Resultado conciliación TESLIAN",
        readonly=True,
        copy=False,
    )

    def action_post(self):
        """
        Valida la conciliación TESLIAN antes de publicar
        facturas de clientes integrados con RED GPS.

        Si la conciliación es válida, guarda en la factura
        un snapshot de la evidencia utilizada para autorizar
        la facturación.
        """

        for move in self:
            partner = move._teslian_validate_billing_reconciliation()

            if partner:
                move._teslian_store_reconciliation_snapshot(
                    partner
                )

        return super().action_post()

    def _teslian_validate_billing_reconciliation(self):
        """
        Comprueba si la factura puede publicarse.

        Devuelve el cliente comercial cuando la factura
        requiere conciliación TESLIAN.

        Devuelve False cuando la regla no aplica.
        """

        self.ensure_one()

        # Solo facturas/notas de crédito de clientes.
        if self.move_type not in (
            "out_invoice",
            "out_refund",
        ):
            return False

        partner = (
            self.partner_id.commercial_partner_id
        )

        # Clientes fuera de RED GPS mantienen
        # el comportamiento estándar de Odoo.
        if not partner.redgps_client_id:
            return False

        reconciliation_is_valid = (
            partner.teslian_billing_status == "matched"
            and partner.teslian_can_invoice
        )

        if reconciliation_is_valid:
            return partner

        status_labels = {
            "not_checked": "Pendiente de validación",
            "matched": "Validado",
            "review": "Requiere revisión",
            "error": "Error de integración",
        }

        status = status_labels.get(
            partner.teslian_billing_status,
            "Estado desconocido",
        )

        message = (
            partner.teslian_reconciliation_message
            or "No existe una conciliación válida."
        )

        raise UserError(
            _(
                "FACTURACIÓN BLOQUEADA POR TESLIAN CONNECT\n\n"
                "Cliente: %(client)s\n"
                "ID RED GPS: %(redgps_client_id)s\n"
                "Estado de conciliación: %(status)s\n"
                "Activos Odoo: %(odoo_assets)s\n"
                "Activos RED GPS: %(redgps_assets)s\n\n"
                "%(message)s\n\n"
                "Debe realizarse una conciliación satisfactoria "
                "con RED GPS antes de publicar esta factura."
            )
            % {
                "client": partner.display_name,
                "redgps_client_id": (
                    partner.redgps_client_id
                ),
                "status": status,
                "odoo_assets": (
                    partner.teslian_odoo_asset_count
                ),
                "redgps_assets": (
                    partner.teslian_redgps_asset_count
                ),
                "message": message,
            }
        )

    def _teslian_store_reconciliation_snapshot(
        self,
        partner,
    ):
        """
        Guarda en la factura la evidencia de conciliación
        utilizada para autorizar su publicación.

        Este snapshot permanece en la factura aunque
        posteriormente cambie la configuración del cliente.
        """

        self.ensure_one()

        self.write({
            "teslian_reconciliation_status": (
                partner.teslian_billing_status
            ),
            "teslian_reconciliation_date": (
                partner.teslian_last_reconciliation
            ),
            "teslian_redgps_client_id": (
                partner.redgps_client_id
            ),
            "teslian_odoo_asset_count": (
                partner.teslian_odoo_asset_count
            ),
            "teslian_redgps_asset_count": (
                partner.teslian_redgps_asset_count
            ),
            "teslian_reconciliation_message": (
                partner.teslian_reconciliation_message
                or ""
            ),
        })