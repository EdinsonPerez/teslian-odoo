from odoo import api, fields, models


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

    def _invalidate_partner_reconciliation(self):
        """
        Invalida la conciliación del cliente cuando cambia
        información relevante de un activo.
        """

        partners = self.mapped("partner_id")

        for partner in partners:
            partner.write({
                "teslian_billing_status": "not_checked",
                "teslian_can_invoice": False,
                "teslian_reconciliation_message": (
                    "La conciliación fue invalidada porque "
                    "se modificó información de los activos."
                ),
                "teslian_missing_in_redgps": False,
                "teslian_missing_in_odoo": False,
                "teslian_redgps_asset_count": 0,
                "teslian_reconciliation_difference": 0,
            })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        records._invalidate_partner_reconciliation()

        return records

    def write(self, vals):
        relevant_fields = {
            "name",
            "partner_id",
            "redgps_asset_id",
            "imei",
            "plate",
            "operational",
        }

        reconciliation_must_be_invalidated = bool(
            relevant_fields.intersection(vals.keys())
        )

        old_partners = self.mapped("partner_id")

        result = super().write(vals)

        if reconciliation_must_be_invalidated:
            new_partners = self.mapped("partner_id")

            partners = (
                old_partners
                | new_partners
            )

            for partner in partners:
                partner.write({
                    "teslian_billing_status": "not_checked",
                    "teslian_can_invoice": False,
                    "teslian_reconciliation_message": (
                        "La conciliación fue invalidada porque "
                        "se modificó información de los activos."
                    ),
                    "teslian_missing_in_redgps": False,
                    "teslian_missing_in_odoo": False,
                    "teslian_redgps_asset_count": 0,
                    "teslian_reconciliation_difference": 0,
                })

        return result

    def unlink(self):
        partners = self.mapped(
            "partner_id"
        )

        result = super().unlink()

        for partner in partners:
            partner.write({
                "teslian_billing_status": "not_checked",
                "teslian_can_invoice": False,
                "teslian_reconciliation_message": (
                    "La conciliación fue invalidada porque "
                    "se eliminó un activo."
                ),
                "teslian_missing_in_redgps": False,
                "teslian_missing_in_odoo": False,
                "teslian_redgps_asset_count": 0,
                "teslian_reconciliation_difference": 0,
            })

        return result