# คู่มือใช้งาน

## 1. โมดูลนี้คืออะไร

โมดูลนี้ช่วยทำงาน “สัญญาแม่” (Contract) ในงานขาย

สัญญา 1 ใบมีได้หลายใบเสนอราคา/ใบขาย (Quotation/Sales Order)

สัญญาปิดได้แม้เก็บเงินไม่ครบ หรือเก็บเงินเกิน

แต่การปิดต้องขออนุมัติเป็นขั้นตอน

## 2. โมดูลนี้ทำอะไรได้บ้าง

- มีเมนูสัญญา `Contracts`
- ผูกสัญญาเข้ากับ `Quotation / Sales Order`
- แนบ `PO ลูกค้า` ไว้กับสัญญา
- ขอปิดสัญญา (Request Close) แบบอนุมัติ
- ขอเปิดสัญญากลับ (Request Re-Activate) แบบอนุมัติ
- ถ้าถูกตีกลับ ต้องกดรับทราบ (Acknowledge) ก่อนจึงขอใหม่ได้

## 3. ต้องเตรียมอะไรก่อน

1. ต้องติดตั้งโมดูลนี้ให้เรียบร้อย
2. ผู้ใช้ต้องมีสิทธิ์กลุ่ม `Contract Request User`
3. ต้องมีการตั้งค่า “ขั้นอนุมัติ” (Tier Validation) โดยแอดมิน

## 4. วิธีใช้งานทีละขั้น

### 4.1 สร้างสัญญา (Contract)

1. ไปที่เมนู `Sales`
2. ไปที่เมนูย่อย `Contracts`
3. กด `Create`
4. ใส่ข้อมูลสำคัญ

- ชื่อสัญญา (Name)
- ลูกค้า (Customer)
- มูลค่าสัญญา (Contract Amount)
- วันเริ่ม / วันจบ
- สถานะ (State)

หมายเหตุ

- ถ้ายังไม่มีสัญญาจริง ให้เลือกสถานะ `No Agreement`
- ถ้ามีสัญญาแล้ว ให้เลือก `Active`

### 4.2 ผูกสัญญาเข้ากับใบขาย (Quotation/Sales Order)

1. เปิด `Quotation` หรือ `Sales Order`
2. ที่ช่อง `Contract` ให้เลือกสัญญาที่ต้องการ

### 4.3 แนบ PO ลูกค้าไว้กับสัญญา

แนวคิด

- PO เก็บไว้ที่สัญญาเป็นหลัก
- ใบขายจะเลือก “PO ที่อยู่ในสัญญาเดียวกัน”
- PO 1 ใบ ใช้กับ SO 1 ใบ

วิธีทำ

1. เปิดสัญญา (Contract)
2. ไปที่แท็บ `Customer PO`
3. เพิ่มบรรทัดใหม่
4. ใส่เลข PO (PO Number)
5. แนบไฟล์ที่ช่อง `Attachment`
6. เลือกใบขายที่เกี่ยวข้องที่ช่อง `Sale Order`

จากนั้น

1. กลับไปที่ `Sales Order`
2. เลือก `Customer PO Document`
3. ระบบจะจำว่า SO ใบนี้อ้าง PO ใบไหน

### 4.4 ขอปิดสัญญา (Request Close)

1. เปิดสัญญาที่สถานะ `Active`
2. กดปุ่ม `Request Close`
3. ระบบจะสร้างเอกสารคำขอให้ 1 ใบ
4. เปิดเอกสารคำขอ
5. กด `Submit`

หลัง Submit

- สถานะสัญญาจะเป็น `Close Pending`
- ระบบจะเริ่มขั้นอนุมัติ

### 4.5 ผู้อนุมัติกด Approve/Reject

1. เปิดเอกสารคำขอ
2. ถ้าคุณเป็นผู้อนุมัติ ระบบจะมีปุ่ม `Approve` และ `Reject`
3. กด `Approve` หรือ `Reject`

หมายเหตุ

- ถ้ากด `Approve` สัญญาจะเป็น `Closed`
- ถ้ากด `Reject` สัญญาจะยังเป็น `Close Pending` อยู่ก่อน

### 4.6 ถ้าถูก Reject ให้ผู้ขอกดรับทราบ (Acknowledge)

1. เปิดเอกสารคำขอที่ถูก reject
2. ผู้ขอต้องกดปุ่ม `Acknowledge`

หลัง Acknowledge

- สัญญาจะกลับเป็น `Active`
- ระบบจะส่งแจ้งเตือนไปหัวหน้าแผนก (ผ่าน activity)
- จากนั้นจึงขอใหม่ได้

### 4.7 ขอเปิดสัญญากลับ (Request Re-Activate)

1. เปิดสัญญาที่สถานะ `Closed`
2. กด `Request Re-Activate`
3. เปิดเอกสารคำขอ
4. กด `Submit`
5. ผู้อนุมัติกด `Approve`

หลังอนุมัติ

- สัญญาจะกลับเป็น `Active`

## 5. สิ่งที่ต้องระวัง

- ถ้าไม่มีสิทธิ์ กลุ่ม `Contract Request User` เมนูและปุ่มจะไม่ขึ้น
- ถ้ายังมีคำขอเก่าที่ยังไม่จบ ระบบจะไม่ให้สร้างคำขอใหม่
- ถ้าถูก reject แล้วไม่กด `Acknowledge` จะขอใหม่ไม่ได้

## 6. ถ้ามีปัญหา

ดูไฟล์ `docs/troubleshooting.md`

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon – Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.
