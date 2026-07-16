# วิธีแก้ปัญหา

## 1. ไม่เห็นเมนู Contracts

สาเหตุที่พบบ่อย

- ผู้ใช้ไม่มีสิทธิ์กลุ่ม `Contract Request User`

วิธีแก้

1. ให้แอดมินไปที่ Users
2. เปิดผู้ใช้คนนั้น
3. เพิ่มกลุ่ม `Contract Request User`
4. รีเฟรชหน้า

## 2. กดปุ่ม Contract Request แล้วขึ้น Permission Error

สาเหตุที่พบบ่อย

- ผู้ใช้กดปุ่มได้ แต่ไม่มีสิทธิ์อ่าน/สร้าง `Contract Status Request`

วิธีแก้

1. ตรวจว่าผู้ใช้มี `Contract Request User`
2. ถ้าเป็นผู้อนุมัติ ให้ตรวจ group ที่ใช้ใน tier ด้วย

## 3. กด Submit แล้วไม่เกิดผู้อนุมัติให้กด

สาเหตุที่พบบ่อย

- ยังไม่ได้ตั้งค่า `tier.definition` ของ model `autoinfo.contract.status.request`
- ตั้งค่า domain ไม่ตรง ทำให้ระบบไม่สร้างรายการอนุมัติ

วิธีแก้

1. ให้แอดมินตรวจ `tier.definition`
2. ตรวจ model ให้เป็น `autoinfo.contract.status.request`
3. ตรวจ domain ให้ตรงกับงานจริง
4. ลองสร้างคำขอใหม่และกด Submit อีกครั้ง

## 4. ปุ่ม Approve / Reject ไม่ขึ้น

สาเหตุที่พบบ่อย

- ผู้ใช้ไม่ใช่คนที่ต้องอนุมัติใน tier
- ยังไม่ถึงลำดับของผู้ใช้นี้

วิธีแก้

1. ตรวจว่าในเอกสารคำขอมี `review_ids` หรือไม่
2. ตรวจว่า user อยู่ใน reviewer ของ tier หรือไม่

## 5. ถูก Reject แล้วขอใหม่ไม่ได้

สาเหตุที่พบบ่อย

- ยังไม่กด `Acknowledge`

วิธีแก้

1. เปิดเอกสารคำขอที่ถูก reject
2. ให้ผู้ขอกด `Acknowledge`
3. จากนั้นสร้างคำขอใหม่ได้

## 6. ไม่มีการแจ้งเตือนไปหัวหน้าแผนกหลัง Acknowledge

สาเหตุที่พบบ่อย

- ใน Contract ไม่มีการใส่ `Department Manager`

วิธีแก้

1. เปิดสัญญา (Contract)
2. ใส่ผู้ใช้ในช่อง `Department Manager`
3. ทดสอบ reject แล้ว acknowledge อีกครั้ง

## 7. ตัวเลข Snapshot เป็น 0

สาเหตุที่พบบ่อย

- ยังไม่มี invoice หรือยังไม่มีการรับเงิน
- invoice ไม่ได้อยู่ในเงื่อนไขที่ระบบคำนวณ

วิธีแก้

1. ตรวจว่ามี invoice ที่เชื่อมกับ SO แล้วหรือไม่
2. ตรวจว่า invoice posted แล้วหรือไม่
3. ตรวจว่ามีการรับชำระแล้วหรือไม่

## 8. แก้ไม่หาย

1. รีสตาร์ต Odoo
2. อัปเกรดโมดูล

ตัวอย่างคำสั่ง

```bash
./odoo-bin -c /etc/odoo/odoo.conf -d <database_name> -u autoinfo_sale_contract_workflow --stop-after-init
```

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon – Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.
