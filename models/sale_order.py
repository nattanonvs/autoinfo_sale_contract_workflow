from odoo import _, fields, models
from odoo.exceptions import AccessError, UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    contract_id = fields.Many2one("autoinfo.contract.agreement", tracking=True)
    contract_state = fields.Selection(related="contract_id.state")
    customer_po_document_id = fields.Many2one(
        "autoinfo.contract.po.document",
        domain="[('contract_id', '=', contract_id)]",
    )

    def action_request_contract_close(self):
        self.ensure_one()
        return self._action_open_contract_request("close", create_if_missing=True)

    def action_request_contract_reactivate(self):
        self.ensure_one()
        return self._action_open_contract_request("reactivate", create_if_missing=True)

    def action_view_contract_request(self):
        self.ensure_one()
        request_type = "reactivate" if self.contract_state == "reopen_pending" else "close"
        return self._action_open_contract_request(request_type, create_if_missing=False)

    def _action_open_contract_request(self, request_type, create_if_missing=False):
        self.ensure_one()
        if not self.user_has_groups(
            "autoinfo_sale_contract_workflow.group_contract_request_user"
        ):
            raise AccessError(
                _("You are not allowed to access a contract request from this sale order.")
            )
        if not self.contract_id:
            raise UserError(_("Please link a contract before creating a request."))

        request = self.env["autoinfo.contract.status.request"].search(
            [
                ("contract_id", "=", self.contract_id.id),
                ("request_type", "=", request_type),
                ("state", "in", ["draft", "submitted", "rejected"]),
            ],
            limit=1,
        )
        if not request and create_if_missing:
            expected_state = "active" if request_type == "close" else "closed"
            if self.contract_id.state != expected_state:
                raise UserError(_("Contract state does not allow this request."))
            request = self.env["autoinfo.contract.status.request"].create(
                {
                    "contract_id": self.contract_id.id,
                    "request_type": request_type,
                }
            )
        if not request:
            raise UserError(_("No active contract request was found for this sale order."))

        return {
            "type": "ir.actions.act_window",
            "name": _("Contract Request"),
            "res_model": "autoinfo.contract.status.request",
            "view_mode": "form",
            "res_id": request.id,
            "target": "current",
        }
