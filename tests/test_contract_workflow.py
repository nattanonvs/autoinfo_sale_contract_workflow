from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from pathlib import Path


@tagged("-at_install", "post_install")
class TestContractWorkflow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        internal_user_group = cls.env.ref("base.group_user")
        contract_group = cls.env.ref(
            "autoinfo_sale_contract_workflow.group_contract_request_user",
            raise_if_not_found=False,
        )
        contract_group_ids = [internal_user_group.id]
        if contract_group:
            contract_group_ids.append(contract_group.id)
        cls.user_requester = cls.env["res.users"].create(
            {
                "name": "Requester",
                "login": "contract_requester",
                "email": "requester@example.com",
                "groups_id": [(6, 0, contract_group_ids)],
            }
        )
        cls.user_reviewer = cls.env["res.users"].create(
            {
                "name": "Reviewer",
                "login": "contract_reviewer",
                "email": "reviewer@example.com",
                "groups_id": [(6, 0, contract_group_ids)],
            }
        )
        cls.user_manager = cls.env["res.users"].create(
            {
                "name": "Manager",
                "login": "contract_manager",
                "email": "manager@example.com",
                "groups_id": [(6, 0, contract_group_ids)],
            }
        )
        cls.user_basic = cls.env["res.users"].create(
            {
                "name": "Basic User",
                "login": "contract_basic_user",
                "email": "basic@example.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            internal_user_group.id,
                            cls.env.ref("sales_team.group_sale_salesman").id,
                        ],
                    )
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Contract Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Contract Service",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 1000.0,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": "Contract Service",
                            "product_uom_qty": 1.0,
                            "price_unit": 1000.0,
                        },
                    )
                ],
            }
        )
        cls.request_model = cls.env["ir.model"]._get("autoinfo.contract.status.request")
        cls.env["tier.definition"].create(
            {
                "name": "Contract Status Request Review",
                "model_id": cls.request_model.id,
                "review_type": "individual",
                "reviewer_id": cls.user_reviewer.id,
                "definition_domain": "[('request_type', 'in', ['close', 'reactivate'])]",
                "approve_sequence": True,
                "sequence": 10,
            }
        )

    def _create_contract(self, state="active"):
        contract = self.env["autoinfo.contract.agreement"].create(
            {
                "name": "Service Agreement 2026",
                "partner_id": self.partner.id,
                "state": state,
                "contract_amount": 1000.0,
                "owner_user_id": self.user_requester.id,
                "department_manager_id": self.user_manager.id,
            }
        )
        self.order.contract_id = contract.id
        return contract

    def test_contract_defaults_to_no_agreement(self):
        contract = self.env["autoinfo.contract.agreement"].create(
            {
                "name": "Service Agreement 2026",
                "partner_id": self.partner.id,
                "state": "no_agreement",
            }
        )
        self.assertEqual(contract.state, "no_agreement")

    def test_sale_order_can_link_contract(self):
        contract = self.env["autoinfo.contract.agreement"].create(
            {
                "name": "Service Agreement 2026",
                "partner_id": self.partner.id,
                "state": "active",
            }
        )
        self.order.contract_id = contract.id
        self.assertEqual(self.order.contract_id, contract)

    def test_sale_order_close_button_creates_contract_request(self):
        contract = self._create_contract(state="active")

        action = self.order.with_user(self.user_requester).action_request_contract_close()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "autoinfo.contract.status.request")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "current")
        request = self.env["autoinfo.contract.status.request"].browse(action["res_id"])
        self.assertTrue(request.exists())
        self.assertEqual(request.contract_id, contract)
        self.assertEqual(request.request_type, "close")

    def test_sale_order_close_button_opens_existing_contract_request(self):
        contract = self._create_contract(state="active")
        request = self.env["autoinfo.contract.status.request"].create(
            {
                "contract_id": contract.id,
                "request_type": "close",
            }
        )

        action = self.order.with_user(self.user_requester).action_request_contract_close()

        self.assertEqual(action["res_id"], request.id)

    def test_sale_order_can_request_reactivate_when_contract_is_closed(self):
        contract = self._create_contract(state="closed")

        action = self.order.with_user(
            self.user_requester
        ).action_request_contract_reactivate()

        self.assertEqual(action["res_model"], "autoinfo.contract.status.request")
        request = self.env["autoinfo.contract.status.request"].browse(action["res_id"])
        self.assertEqual(request.contract_id, contract)
        self.assertEqual(request.request_type, "reactivate")

    def test_sale_order_close_request_rejects_wrong_contract_state(self):
        contract = self._create_contract(state="closed")

        with self.assertRaises(UserError):
            self.order.with_user(self.user_requester).action_request_contract_close()

        request = self.env["autoinfo.contract.status.request"].search(
            [
                ("contract_id", "=", contract.id),
                ("request_type", "=", "close"),
            ],
            limit=1,
        )
        self.assertFalse(request)

    def test_sale_order_views_existing_close_request_when_contract_is_pending(self):
        contract = self._create_contract(state="close_pending")
        request = self.env["autoinfo.contract.status.request"].create(
            {
                "contract_id": contract.id,
                "request_type": "close",
                "state": "submitted",
            }
        )

        action = self.order.with_user(self.user_requester).action_view_contract_request()

        self.assertEqual(action["res_id"], request.id)

    def test_sale_order_views_existing_reactivate_request_when_contract_reopens(self):
        contract = self._create_contract(state="reopen_pending")
        request = self.env["autoinfo.contract.status.request"].create(
            {
                "contract_id": contract.id,
                "request_type": "reactivate",
                "state": "submitted",
            }
        )

        action = self.order.with_user(self.user_requester).action_view_contract_request()

        self.assertEqual(action["res_id"], request.id)

    def test_sale_order_form_replaces_legacy_close_button(self):
        form_arch = self.env["sale.order"].fields_view_get(view_type="form")["arch"]

        self.assertIn('name="action_request_contract_close"', form_arch)
        self.assertIn('name="action_view_contract_request"', form_arch)
        self.assertIn('name="action_request_contract_reactivate"', form_arch)
        self.assertNotIn('name="action_open_close_agreement_wizard"', form_arch)

    def test_sale_order_close_button_is_scoped_to_contract_request_group(self):
        view = self.env.ref(
            "autoinfo_sale_contract_workflow.view_order_form_contract_request_bridge"
        )

        self.assertIn(
            'groups="autoinfo_sale_contract_workflow.group_contract_request_user"',
            view.arch_db,
        )

    def test_sale_order_close_action_requires_contract_request_group(self):
        contract = self._create_contract(state="active")

        with self.assertRaises(AccessError):
            self.order.with_user(self.user_basic).action_request_contract_close()

        self.assertEqual(contract.state, "active")

    def test_contract_request_security_group_scopes_access(self):
        group = self.env.ref(
            "autoinfo_sale_contract_workflow.group_contract_request_user"
        )
        agreement_access = self.env.ref(
            "autoinfo_sale_contract_workflow.access_contract_agreement_user"
        )
        request_access = self.env.ref(
            "autoinfo_sale_contract_workflow.access_contract_status_request_user"
        )
        po_access = self.env.ref(
            "autoinfo_sale_contract_workflow.access_contract_po_document_user"
        )

        self.assertIn(group, self.user_requester.groups_id)
        self.assertEqual(agreement_access.group_id, group)
        self.assertEqual(request_access.group_id, group)
        self.assertEqual(po_access.group_id, group)
        with self.assertRaises(AccessError):
            self.env["autoinfo.contract.agreement"].with_user(self.user_basic).create(
                {
                    "name": "Restricted Agreement",
                    "partner_id": self.partner.id,
                    "state": "active",
                }
            )

    def test_contract_tree_view_shows_end_date_and_state_badge(self):
        tree_view = self.env.ref(
            "autoinfo_sale_contract_workflow.view_contract_agreement_tree"
        )

        self.assertIn('name="date_end"', tree_view.arch_db)
        self.assertIn('name="state" widget="badge"', tree_view.arch_db)

    def test_contract_form_view_has_grouped_request_actions_and_history(self):
        form_view = self.env.ref(
            "autoinfo_sale_contract_workflow.view_contract_agreement_form"
        )

        self.assertIn('name="action_create_close_request"', form_view.arch_db)
        self.assertIn('name="action_create_reactivate_request"', form_view.arch_db)
        self.assertIn(
            'groups="autoinfo_sale_contract_workflow.group_contract_request_user"',
            form_view.arch_db,
        )
        self.assertIn("Request History", form_view.arch_db)
        self.assertIn('name="status_request_ids"', form_view.arch_db)
        self.assertIn('name="requested_by_id"', form_view.arch_db)

    def test_request_form_view_shows_explicit_statusbar_and_tier_widget(self):
        form_view = self.env.ref(
            "autoinfo_sale_contract_workflow.view_contract_status_request_form"
        )

        self.assertIn(
            'statusbar_visible="draft,submitted,approved,rejected,acknowledged"',
            form_view.arch_db,
        )
        self.assertIn('name="review_ids" widget="tier_validation"', form_view.arch_db)
        self.assertIn('name="action_acknowledge"', form_view.arch_db)

    def test_static_description_declares_utf8_for_thai_content(self):
        module_root = Path(__file__).resolve().parents[1]
        description_html = (module_root / "static" / "description" / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn('<meta charset="utf-8"/>', description_html)
        self.assertIn("โมดูลนี้เพิ่ม Contract แบบศูนย์กลาง", description_html)
        self.assertNotIn("à¸", description_html)

    def test_contract_form_buttons_create_close_and_reactivate_requests(self):
        active_contract = self._create_contract(state="active")
        close_action = active_contract.action_create_close_request()
        close_request = self.env["autoinfo.contract.status.request"].browse(
            close_action["res_id"]
        )

        self.assertEqual(close_action["res_model"], "autoinfo.contract.status.request")
        self.assertEqual(close_request.contract_id, active_contract)
        self.assertEqual(close_request.request_type, "close")

        closed_contract = self._create_contract(state="closed")
        reactivate_action = closed_contract.action_create_reactivate_request()
        reactivate_request = self.env["autoinfo.contract.status.request"].browse(
            reactivate_action["res_id"]
        )

        self.assertEqual(
            reactivate_action["res_model"], "autoinfo.contract.status.request"
        )
        self.assertEqual(reactivate_request.contract_id, closed_contract)
        self.assertEqual(reactivate_request.request_type, "reactivate")

    def test_po_document_keeps_single_attachment_and_links_one_sale_order(self):
        contract = self.env["autoinfo.contract.agreement"].create(
            {"name": "Agreement A", "partner_id": self.partner.id, "state": "active"}
        )
        attachment = self.env["ir.attachment"].create(
            {
                "name": "PO-001.pdf",
                "datas": "UERG",
                "res_model": "autoinfo.contract.agreement",
                "res_id": contract.id,
                "type": "binary",
            }
        )
        po_doc = self.env["autoinfo.contract.po.document"].create(
            {
                "contract_id": contract.id,
                "attachment_id": attachment.id,
                "po_number": "PO-001",
                "sale_order_id": self.order.id,
            }
        )
        self.assertEqual(po_doc.attachment_id, attachment)
        self.assertEqual(po_doc.sale_order_id, self.order)
        self.assertEqual(po_doc.contract_id, contract)

    def test_submit_close_request_moves_contract_to_close_pending(self):
        contract = self._create_contract(state="active")
        request = self.env["autoinfo.contract.status.request"].with_user(
            self.user_requester
        ).create(
            {
                "contract_id": contract.id,
                "request_type": "close",
            }
        )

        request.action_submit()

        self.assertEqual(request.state, "submitted")
        self.assertEqual(contract.state, "close_pending")
        self.assertEqual(request.contract_amount_snapshot, 1000.0)
        self.assertEqual(request.invoice_amount_snapshot, 0.0)
        self.assertEqual(request.paid_amount_snapshot, 0.0)
        self.assertTrue(request.review_ids)
        self.assertFalse(request.validated)

    def test_approve_close_request_closes_contract(self):
        contract = self._create_contract(state="active")
        request = self.env["autoinfo.contract.status.request"].with_user(
            self.user_requester
        ).create(
            {
                "contract_id": contract.id,
                "request_type": "close",
            }
        )
        request.action_submit()

        request.with_user(self.user_reviewer).action_approve()
        request.invalidate_cache()
        contract.invalidate_cache()

        self.assertEqual(request.state, "approved")
        self.assertTrue(request.validated)
        self.assertEqual(contract.state, "closed")
        self.assertEqual(request.review_ids.mapped("status"), ["approved"])

    def test_reject_then_acknowledge_allows_new_request(self):
        contract = self._create_contract(state="active")
        request = self.env["autoinfo.contract.status.request"].with_user(
            self.user_requester
        ).create(
            {
                "contract_id": contract.id,
                "request_type": "close",
            }
        )
        request.action_submit()

        request.with_user(self.user_reviewer).action_reject()
        request.invalidate_cache()
        contract.invalidate_cache()

        self.assertEqual(request.state, "rejected")
        self.assertTrue(request.rejected)
        self.assertEqual(contract.state, "close_pending")
        with self.assertRaises(ValidationError):
            self.env["autoinfo.contract.status.request"].create(
                {
                    "contract_id": contract.id,
                    "request_type": "close",
                }
            )

        request.with_user(self.user_requester).action_acknowledge()
        request.invalidate_cache()
        manager_activity = self.env["mail.activity"].search(
            [
                ("res_model", "=", "autoinfo.contract.agreement"),
                ("res_id", "=", contract.id),
                ("user_id", "=", self.user_manager.id),
            ],
            limit=1,
        )

        self.assertEqual(request.state, "acknowledged")
        self.assertEqual(contract.state, "active")
        self.assertTrue(manager_activity)
        second_request = self.env["autoinfo.contract.status.request"].create(
            {
                "contract_id": contract.id,
                "request_type": "close",
            }
        )
        self.assertTrue(second_request)

    def test_acknowledge_creates_manager_activity_with_resubmit_note(self):
        contract = self._create_contract(state="active")
        request = self.env["autoinfo.contract.status.request"].with_user(
            self.user_requester
        ).create(
            {
                "contract_id": contract.id,
                "request_type": "close",
            }
        )
        request.action_submit()
        request.with_user(self.user_reviewer).action_reject()

        request.with_user(self.user_requester).action_acknowledge()
        activity = self.env["mail.activity"].search(
            [
                ("res_model", "=", "autoinfo.contract.agreement"),
                ("res_id", "=", contract.id),
                ("user_id", "=", self.user_manager.id),
            ],
            limit=1,
        )

        self.assertTrue(activity)
        self.assertIn("A new request can now be created.", activity.note)

    def test_acknowledge_without_manager_restores_contract_and_allows_resubmit(self):
        contract = self.env["autoinfo.contract.agreement"].create(
            {
                "name": "Agreement Without Manager",
                "partner_id": self.partner.id,
                "state": "active",
                "owner_user_id": self.user_requester.id,
            }
        )
        request = self.env["autoinfo.contract.status.request"].with_user(
            self.user_requester
        ).create(
            {
                "contract_id": contract.id,
                "request_type": "close",
            }
        )
        request.action_submit()
        request.with_user(self.user_reviewer).action_reject()

        request.with_user(self.user_requester).action_acknowledge()
        activities = self.env["mail.activity"].search(
            [
                ("res_model", "=", "autoinfo.contract.agreement"),
                ("res_id", "=", contract.id),
            ]
        )
        second_request = self.env["autoinfo.contract.status.request"].create(
            {
                "contract_id": contract.id,
                "request_type": "close",
            }
        )

        self.assertEqual(request.state, "acknowledged")
        self.assertEqual(contract.state, "active")
        self.assertFalse(activities)
        self.assertTrue(second_request)

    def test_approve_reactivate_request_reopens_contract(self):
        contract = self._create_contract(state="closed")
        request = self.env["autoinfo.contract.status.request"].with_user(
            self.user_requester
        ).create(
            {
                "contract_id": contract.id,
                "request_type": "reactivate",
            }
        )

        request.action_submit()
        request.with_user(self.user_reviewer).action_approve()
        request.invalidate_cache()
        contract.invalidate_cache()

        self.assertEqual(request.state, "approved")
        self.assertEqual(contract.state, "active")
