from odoo import fields, models


class ContractPoDocument(models.Model):
    _name = "autoinfo.contract.po.document"
    _description = "Contract Customer PO Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    contract_id = fields.Many2one(
        "autoinfo.contract.agreement",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    attachment_id = fields.Many2one("ir.attachment", required=True, ondelete="restrict")
    po_number = fields.Char(required=True, tracking=True)
    po_date = fields.Date()
    po_amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        related="contract_id.currency_id",
        store=True,
        readonly=True,
    )
    sale_order_id = fields.Many2one("sale.order", ondelete="set null")

    _sql_constraints = [
        (
            "contract_po_sale_order_uniq",
            "unique(sale_order_id)",
            "A sale order can link to only one customer PO document.",
        )
    ]
