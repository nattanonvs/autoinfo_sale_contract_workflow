# Changelog

## 15.0.1.0.1 (2026-07-16)

- เพิ่มสัญญาแม่ (Contract) และสถานะ 5 ค่า: No Agreement / Active / Close Pending / Closed / Reopen Pending
- เพิ่มคำขอเปลี่ยนสถานะสัญญา (Close / Re-Activate) และทำงานร่วมกับ Tier Validation
- ปรับปุ่มบน Sale Order ให้เป็น entry point ของคำขอ ตามสถานะสัญญา และกันการปิดสัญญาตรงแบบเดิม
- เพิ่มสิทธิ์กลุ่ม `Contract Request User` เพื่อคุมการใช้งาน Contract/Request/PO Document
- เพิ่มเอกสารใน `docs/` (user_guide, technical_guide, troubleshooting, installation_guide)
- เพิ่มไฟล์ release สำหรับ Odoo Apps ใน `static/description/` พร้อมโลโก้และคำอธิบายโมดูล
- เพิ่ม `.gitignore` เพื่อกันไฟล์ชั่วคราวและไฟล์แพ็กเกจหลุดเข้า repository

## Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon – Project conception, implementation, and thorough review of all deliverables.

AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight.
