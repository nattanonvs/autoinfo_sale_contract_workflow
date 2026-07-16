# คู่มือติดตั้ง

<p style="color:red;"><strong>คำเตือนสำคัญ:</strong> ถ้า path โมดูลนี้ไม่อยู่ใน <code>addons_path</code>, หรือยังไม่ได้ติดตั้ง dependency เช่น <code>base_tier_validation</code> และ <code>autoinfo_sale_order_invoice_amount</code>, Odoo อาจโหลดโมดูลไม่ขึ้น, ผู้ใช้เข้าเมนูไม่ได้, หรือ service ล้มตอนอัปเดตโมดูลได้</p>

<p style="color:red;"><strong>คำเตือนสำคัญ:</strong> ห้ามอัปเกรดบน production โดยตรงในช่วงเวลาที่มีผู้ใช้ทำงานอยู่ ถ้ายังไม่ได้สำรองฐานข้อมูลและยังไม่ได้ทดสอบบน staging ก่อน</p>

## 1. ข้อมูลที่ใช้ในงานนี้

- path ติดตั้ง: `/var/odoo/custom15_autoinfo`
- repo: `https://github.com/nattanonvs/autoinfo_sale_contract_workflow.git`
- ชื่อโมดูล: `autoinfo_sale_contract_workflow`

## 2. ตรวจของก่อนติดตั้ง

ต้องมีสิ่งนี้ก่อน:

- Odoo 15
- PostgreSQL ใช้งานได้ปกติ
- สิทธิ์เขียนไฟล์ใน `/var/odoo/custom15_autoinfo`
- โมดูล dependency อยู่ใน `addons_path`

dependency ที่ต้องมี:

- `sale_management`
- `crm`
- `mail`
- `base_tier_validation`
- `autoinfo_sale_order_invoice_amount`

## 3. สำรองข้อมูลก่อน

ก่อนติดตั้งหรืออัปเกรด ให้ทำอย่างน้อย 3 อย่าง:

1. สำรองฐานข้อมูล
2. สำรองโฟลเดอร์โมดูลเดิม
3. จดค่า `addons_path` และ service name ของ Odoo

## 4. ติดตั้งจาก Git

### 4.1 clone repo

```bash
cd /var/odoo/custom15_autoinfo
git clone https://github.com/nattanonvs/autoinfo_sale_contract_workflow.git
```

### 4.2 ตรวจโครงสร้างไฟล์

ต้องมีไฟล์สำคัญอย่างน้อย:

- `__manifest__.py`
- `models/`
- `views/`
- `security/`
- `docs/`

### 4.3 ตรวจ addons_path

ตรวจว่า `/var/odoo/custom15_autoinfo` อยู่ใน `addons_path`

ตัวอย่าง:

```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/var/odoo/custom15_autoinfo
```

## 5. รีสตาร์ต Odoo

ตัวอย่าง:

```bash
sudo systemctl restart odoo
sudo systemctl status odoo
```

หรือถ้าใช้ service name อื่น ให้ใช้ชื่อ service จริงของเครื่อง

## 6. ติดตั้งโมดูลครั้งแรก

### 6.1 ผ่านหน้า Apps

1. เข้า Odoo ด้วยผู้ใช้ที่มีสิทธิ์ Settings
2. ไปที่ `Apps`
3. กด `Update Apps List`
4. ค้นหา `AUTO-INFO : Sale Contract Workflow`
5. กด `Install`

### 6.2 ผ่าน command line

```bash
./odoo-bin -c /etc/odoo/odoo.conf -d <database_name> -i autoinfo_sale_contract_workflow --stop-after-init
```

## 7. อัปเกรดโมดูล

ใช้เมื่อมีไฟล์ใหม่จาก repo หรือ zip

```bash
cd /var/odoo/custom15_autoinfo/autoinfo_sale_contract_workflow
git pull
```

จากนั้น:

```bash
./odoo-bin -c /etc/odoo/odoo.conf -d <database_name> -u autoinfo_sale_contract_workflow --stop-after-init
```

## 8. ตั้งค่าหลังติดตั้ง

### 8.1 สิทธิ์ผู้ใช้

ผู้ใช้ที่ต้องใช้งานโมดูลนี้ ต้องมี group:

- `Contract Request User`

### 8.2 ตั้ง Tier Validation

ต้องตั้ง `tier.definition` ให้กับ model:

- `autoinfo.contract.status.request`

ถ้ายังไม่ตั้ง:

- ปุ่ม `Submit` อาจทำงานได้
- แต่จะไม่มีคนอนุมัติ
- และ workflow จะไม่สมบูรณ์

### 8.3 ตรวจเมนู

หลังติดตั้งแล้ว ควรเห็นเมนู:

- `Contracts`
- `Customer PO Documents`

## 9. ตรวจหลังติดตั้ง

ทดสอบอย่างน้อย:

1. สร้าง Contract 1 ใบ
2. สร้าง Sales Order 1 ใบ แล้วผูก Contract
3. กด `Contract Request`
4. กด `Submit`
5. ทดสอบ `Approve` หรือ `Reject`
6. ถ้า reject ให้กด `Acknowledge`

## 10. อาการที่ต้องหยุดทันที

หยุดและ rollback ถ้าเจอ:

- Odoo start ไม่ขึ้นหลัง restart
- หน้าเว็บขึ้น error หลังติดตั้ง
- เข้าเมนู `Contracts` แล้ว Permission Error ทั้งที่ให้ group แล้ว
- กด `Submit` แล้ว request หาย หรือ state contract ไม่เปลี่ยน
- มี error จาก dependency ใน log ตอนโหลดโมดูล

## 11. rollback แบบย่อ

1. restore database backup
2. restore โฟลเดอร์โมดูลเก่า
3. restart Odoo

## 12. เอกสารที่เกี่ยวข้อง

- `README.md`
- `docs/user_guide.md`
- `docs/technical_guide.md`
- `docs/troubleshooting.md`
- `docs/changelog.md`

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon – Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.
