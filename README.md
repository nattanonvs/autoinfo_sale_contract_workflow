# AUTO-INFO : Sale Contract Workflow

โมดูลนี้ใช้จัดการ “สัญญาแม่” (Contract) สำหรับงานขายใน Odoo 15

เป้าหมายคือแยกการปิดสัญญาออกจาก `Quotation / Sales Order` แล้วเปลี่ยนเป็น workflow แบบขออนุมัติ

รองรับกรณีงานจริงที่:

- 1 สัญญา มีหลาย `Customer PO`
- 1 สัญญา มีหลาย `Quotation / Sales Order`
- ปิดสัญญาได้แม้ยอดเก็บจริงไม่ครบ หรือเกิน
- เปิดสัญญากลับได้ แต่ต้องขออนุมัติใหม่

## ฟีเจอร์หลัก

- เพิ่มโมเดล `Contract`
- เพิ่มโมเดล `Contract Status Request`
- เพิ่มโมเดล `Customer PO Document`
- ใช้ `Tier Validation` กับคำขอ `Close` และ `Re-Activate`
- เปลี่ยนปุ่มบน `Sales Order` ให้เป็น entry point ของคำขอ แทนการปิดสัญญาตรง
- รองรับ `Reject -> Acknowledge -> Request ใหม่`
- บันทึก `Snapshot` ของตัวเลขสำคัญตอนส่งคำขอ

## สถานะของ Contract

- `No Agreement`
- `Active`
- `Close Pending`
- `Closed`
- `Reopen Pending`

## Dependency

- `sale_management`
- `crm`
- `mail`
- `base_tier_validation`
- `autoinfo_sale_order_invoice_amount`

## การติดตั้งจาก Git

ปลายทางที่ต้องใช้ในเอกสารชุดนี้:

- path: `/var/odoo/custom15_autoinfo`
- repo: `https://github.com/nattanonvs/autoinfo_sale_contract_workflow.git`

ตัวอย่าง:

```bash
cd /var/odoo/custom15_autoinfo
git clone https://github.com/nattanonvs/autoinfo_sale_contract_workflow.git
```

ดูรายละเอียดแบบเต็มใน:

- `docs/installation_guide.md`

## เอกสาร

- คู่มือใช้งาน: `docs/user_guide.md`
- คู่มือเทคนิค: `docs/technical_guide.md`
- วิธีติดตั้ง: `docs/installation_guide.md`
- วิธีแก้ปัญหา: `docs/troubleshooting.md`
- ประวัติการเปลี่ยนแปลง: `docs/changelog.md`

## คำอธิบายสั้นสำหรับ Repo

Odoo 15 module for master sale contracts, close/reactivate approval requests, PO document linking, and tier validation workflow.

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon – Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.
