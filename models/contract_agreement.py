from odoo import _, fields, models
from odoo.exceptions import UserError


class ContractAgreement(models.Model):
    _name = "autoinfo.contract.agreement"
    _description = "AutoInfo Contract Agreement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)
    contract_no = fields.Char(copy=False, tracking=True)
    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    opportunity_id = fields.Many2one("crm.lead", tracking=True)
    owner_user_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, tracking=True
    )
    department_manager_id = fields.Many2one("res.users")
    date_start = fields.Date()
    date_end = fields.Date()
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    contract_amount = fields.Monetary(currency_field="currency_id", tracking=True)
    state = fields.Selection(
        [
            ("no_agreement", "No Agreement"),
            ("active", "Active"),
            ("close_pending", "Close Pending"),
            ("closed", "Closed"),
            ("reopen_pending", "Reopen Pending"),
        ],
        default="no_agreement",
        required=True,
        tracking=True,
    )
    sale_order_ids = fields.One2many("sale.order", "contract_id")
    status_request_ids = fields.One2many(
        "autoinfo.contract.status.request", "contract_id"
    )
    customer_po_document_ids = fields.One2many(
        "autoinfo.contract.po.document", "contract_id"
    )

    def _action_open_status_request(self, request_type, allowed_state):
        self.ensure_one()
        if self.state != allowed_state:
            raise UserError(_("Contract state does not allow this request."))

        request = self.env["autoinfo.contract.status.request"].search(
            [
                ("contract_id", "=", self.id),
                ("request_type", "=", request_type),
                ("state", "in", ["draft", "submitted", "rejected"]),
            ],
            limit=1,
        )
        if not request:
            request = self.env["autoinfo.contract.status.request"].create(
                {
                    "contract_id": self.id,
                    "request_type": request_type,
                }
            )

        return {
            "type": "ir.actions.act_window",
            "name": _("Contract Request"),
            "res_model": "autoinfo.contract.status.request",
            "view_mode": "form",
            "res_id": request.id,
            "target": "current",
        }

    def action_create_close_request(self):
        return self._action_open_status_request("close", "active")

    def action_create_reactivate_request(self):
        return self._action_open_status_request("reactivate", "closed")
