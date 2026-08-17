from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        """
        Impide publicar facturas de clientes que no tengan
        una conciliación válida entre Odoo y RED GPS.

        La factura puede permanecer en borrador para revisión,
        pero no puede contabilizarse mientras la conciliación
        TESLIAN no esté aprobada.
        """

        for move in self:
            move._teslian_validate_billing_reconciliation()

        return super().action_post()

    def _teslian_validate_billing_reconciliation(self):
        """
        Valida si la factura requiere conciliación TESLIAN
        antes de permitir su publicación.
        """

        self.ensure_one()

        # Solo aplicamos la regla a facturas y notas
        # comerciales de clientes.
        if self.move_type not in (
            "out_invoice",
            "out_refund",
        ):
            return

        partner = self.partner_id.commercial_partner_id

        # Si el cliente no está integrado con RED GPS,
        # esta regla no aplica.
        if not partner.redgps_client_id:
            return

        if (
            partner.teslian_billing_status == "matched"
            and partner.teslian_can_invoice
        ):
            return

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
                "Estado de conciliación: %(status)s\n"
                "Activos Odoo: %(odoo_assets)s\n"
                "Activos RED GPS: %(redgps_assets)s\n\n"
                "%(message)s\n\n"
                "Debe realizarse una conciliación satisfactoria "
                "con RED GPS antes de publicar esta factura."
            )
            % {
                "client": partner.display_name,
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