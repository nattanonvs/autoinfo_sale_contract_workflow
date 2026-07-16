from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ContractStatusRequest(models.Model):
    _name = "autoinfo.contract.status.request"
    _description = "Contract Status Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "tier.validation"]
    _order = "id desc"

    _state_field = "validation_state"
    _state_from = ["submitted"]
    _state_to = ["approved"]
    _tier_validation_manual_config = True

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: _("New"),
        tracking=True,
    )
    contract_id = fields.Many2one(
        "autoinfo.contract.agreement",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    request_type = fields.Selection(
        [("close", "Close"), ("reactivate", "Reactivate")],
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("acknowledged", "Acknowledged"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    validation_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
        ],
        default="draft",
        required=True,
        copy=False,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="contract_id.currency_id",
        store=True,
        readonly=True,
    )
    requested_by_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True,
    )
    submitted_at = fields.Datetime(readonly=True)
    approved_by_id = fields.Many2one("res.users", readonly=True)
    approved_at = fields.Datetime(readonly=True)
    rejected_by_id = fields.Many2one("res.users", readonly=True)
    rejected_at = fields.Datetime(readonly=True)
    acknowledged_by_id = fields.Many2one("res.users", readonly=True)
    acknowledged_at = fields.Datetime(readonly=True)
    contract_amount_snapshot = fields.Monetary(currency_field="currency_id", readonly=True)
    invoice_amount_snapshot = fields.Monetary(currency_field="currency_id", readonly=True)
    paid_amount_snapshot = fields.Monetary(currency_field="currency_id", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].sudo().next_by_code(
                    "autoinfo.contract.status.request"
                ) or _("New")
        return super().create(vals_list)

    @api.constrains("contract_id", "state")
    def _check_single_open_request(self):
        terminal_states = ("approved", "acknowledged")
        for request in self:
            if not request.contract_id or request.state in terminal_states:
                continue
            open_requests = self.search(
                [
                    ("contract_id", "=", request.contract_id.id),
                    ("state", "not in", terminal_states),
                    ("id", "!=", request.id),
                ],
                limit=1,
            )
            if open_requests:
                raise ValidationError(
                    _(
                        "A contract can only have one status request pending or awaiting acknowledgement at a time."
                    )
                )

    def _get_under_validation_exceptions(self):
        return super()._get_under_validation_exceptions() + [
            "state",
            "approved_by_id",
            "approved_at",
            "rejected_by_id",
            "rejected_at",
            "acknowledged_by_id",
            "acknowledged_at",
        ]

    def _get_review_target_state(self):
        self.ensure_one()
        if self.request_type == "close":
            return "closed"
        return "active"

    def _get_pending_contract_state(self):
        self.ensure_one()
        if self.request_type == "close":
            return "close_pending"
        return "reopen_pending"

    def _get_reverted_contract_state(self):
        self.ensure_one()
        if self.request_type == "close":
            return "active"
        return "closed"

    def _validate_request_type(self):
        self.ensure_one()
        expected_contract_state = "active" if self.request_type == "close" else "closed"
        if self.contract_id.state != expected_contract_state:
            raise ValidationError(
                _(
                    "Contract state does not match the requested operation."
                )
            )

    def _compute_snapshot_values(self):
        self.ensure_one()
        sale_orders = self.contract_id.sudo().sale_order_ids
        return {
            "contract_amount_snapshot": self.contract_id.contract_amount,
            "invoice_amount_snapshot": sum(sale_orders.mapped("total_invoice_amount")),
            "paid_amount_snapshot": sum(sale_orders.mapped("total_paid_amount")),
        }

    def action_submit(self):
        for request in self:
            if request.state != "draft":
                raise ValidationError(_("Only draft requests can be submitted."))
            request._validate_request_type()
            snapshot_vals = request._compute_snapshot_values()
            request.write(
                {
                    "state": "submitted",
                    "validation_state": "submitted",
                    "submitted_at": fields.Datetime.now(),
                    **snapshot_vals,
                }
            )
            request.contract_id.write({"state": request._get_pending_contract_state()})
            request.request_validation()
            request.invalidate_cache()
        return True

    def action_approve(self):
        for request in self:
            if request.state != "submitted":
                raise ValidationError(_("Only submitted requests can be approved."))
            request.validate_tier()
            request.invalidate_cache()
            if request.validated:
                request.write(
                    {
                        "state": "approved",
                        "validation_state": "approved",
                        "approved_by_id": self.env.user.id,
                        "approved_at": fields.Datetime.now(),
                    }
                )
                request.contract_id.write({"state": request._get_review_target_state()})
        return True

    def action_reject(self):
        for request in self:
            if request.state != "submitted":
                raise ValidationError(_("Only submitted requests can be rejected."))
            request.reject_tier()
            request.invalidate_cache()
            if request.rejected:
                request.write(
                    {
                        "state": "rejected",
                        "rejected_by_id": self.env.user.id,
                        "rejected_at": fields.Datetime.now(),
                    }
                )
        return True

    def action_acknowledge(self):
        for request in self:
            if request.state != "rejected":
                raise ValidationError(_("Only rejected requests can be acknowledged."))
            if request.requested_by_id and request.requested_by_id != self.env.user:
                raise ValidationError(_("Only the requester can acknowledge a rejection."))
            request.write(
                {
                    "state": "acknowledged",
                    "acknowledged_by_id": self.env.user.id,
                    "acknowledged_at": fields.Datetime.now(),
                }
            )
            request.contract_id.write({"state": request._get_reverted_contract_state()})
            if request.contract_id.department_manager_id:
                request.contract_id.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=request.contract_id.department_manager_id.id,
                    note=_(
                        "A rejected contract request was acknowledged. A new request can now be created."
                    ),
                )
        return True
