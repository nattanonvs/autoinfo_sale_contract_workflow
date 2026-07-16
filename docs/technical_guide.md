# คู่มือเทคนิค

## 1. โมดูลนี้ทำอะไร

โมดูลนี้เพิ่ม “สัญญาแม่” (Contract) และ “คำขอเปลี่ยนสถานะสัญญา” (Request)

เป้าหมายคือไม่ให้ปิดสัญญาตรงที่ `Sale Order`

ให้เปลี่ยนเป็น

- ขอปิด (Request Close)
- อนุมัติ (Tier Validation)
- ปิดสัญญา (Closed)

และมี flow เปิดกลับแบบเดียวกัน

## 2. Dependency หลัก

- `sale_management`
- `crm`
- `mail`
- `base_tier_validation`
- `autoinfo_sale_order_invoice_amount`

หมายเหตุ

- โมดูล `autoinfo_sale_order_invoice_amount` ยังเป็นแหล่งตัวเลข invoice/paid ที่ใช้ทำ snapshot ใน request

## 3. โครงสร้างไฟล์

- `__manifest__.py`
- `models/`
  - `contract_agreement.py`
  - `contract_po_document.py`
  - `contract_status_request.py`
  - `sale_order.py`
  - `tier_definition.py`
- `views/`
  - `contract_agreement_views.xml`
  - `contract_po_document_views.xml`
  - `contract_status_request_views.xml`
  - `sale_order_views.xml`
- `security/`
  - `security.xml`
  - `ir.model.access.csv`
- `data/`
  - `ir_sequence_data.xml`
- `tests/`
  - `test_contract_workflow.py`
- `docs/`
  - `user_guide.md`
  - `technical_guide.md`
  - `troubleshooting.md`

## 4. โมเดลหลัก

### 4.1 Contract

Model: `autoinfo.contract.agreement`

State (สถานะธุรกิจ)

- `no_agreement`
- `active`
- `close_pending`
- `closed`
- `reopen_pending`

### 4.2 Customer PO Document

Model: `autoinfo.contract.po.document`

แนวคิด

- เก็บไฟล์ PO เป็น `ir.attachment`
- PO 1 ใบผูกกับ SO ได้ 1 ใบ

### 4.3 Contract Status Request

Model: `autoinfo.contract.status.request`

Request Type

- `close`
- `reactivate`

State (สถานะของคำขอ)

- `draft`
- `submitted`
- `approved`
- `rejected`
- `acknowledged`

Tier Validation

- โมเดลนี้ inherit `tier.validation`
- เริ่มขั้นอนุมัติตอนกด `Submit` ผ่าน `request_validation()`
- ปุ่ม `Approve/Reject` เรียก `validate_tier()/reject_tier()` และ sync สถานะของ request

## 5. Security

Group

- `Contract Request User`

ACL

- `autoinfo.contract.agreement`
- `autoinfo.contract.po.document`
- `autoinfo.contract.status.request`

หมายเหตุ

- ถ้าผู้ใช้ไม่มี group นี้ จะอ่าน/สร้าง/แก้ไข 3 โมเดลนี้ไม่ได้

## 6. การตั้งค่า Tier Validation

ต้องสร้าง `tier.definition` สำหรับ model:

- `autoinfo.contract.status.request`

ตัวอย่างแนวคิด (ไม่ใช่โค้ดตายตัว)

- กำหนด reviewer ตามเงื่อนไข
  - request_type = close
  - มูลค่าสัญญามากกว่า X

## 7. การติดตั้งและอัปเดต

### 7.1 วางโฟลเดอร์

1. วางโฟลเดอร์ `autoinfo_sale_contract_workflow` ไว้ใน addons_path
2. รีสตาร์ต Odoo
3. ไปที่ Apps แล้วกด Update Apps List
4. ค้นหาโมดูล แล้วกด Install

### 7.2 อัปเดต (Upgrade)

1. คัดลอกไฟล์ใหม่ทับของเดิม
2. รีสตาร์ต Odoo
3. อัปเกรดโมดูล

ตัวอย่างคำสั่ง

```bash
./odoo-bin -c /etc/odoo/odoo.conf -d <database_name> -u autoinfo_sale_contract_workflow --stop-after-init
```

## 8. การทดสอบ

มีเทสต์ใน `tests/test_contract_workflow.py`

แนวที่เทสต์ครอบคลุม

- สร้าง contract/po/request ได้
- ขอปิด -> ส่งอนุมัติ -> approve แล้ว contract ปิด
- reject แล้วยังสร้าง request ใหม่ไม่ได้จนกว่าจะ acknowledge
- acknowledge แล้วมี activity ไปหัวหน้าแผนก
- ปุ่มบน SO เปลี่ยนเป็น entry point ของ request แทน legacy close

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon – Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.
