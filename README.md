# 📄 Karaoke Invoice Monitoring System

Hệ thống tự động theo dõi file **.PRN** và **.PNG**, chuyển đổi – OCR hóa đơn, gửi thông báo Telegram và **phát hiện sai phạm chênh lệch tiền** giữa hóa đơn *Tạm tính* và *Thanh toán*.

---

## 🚀 TÍNH NĂNG CHÍNH

- 👀 Theo dõi thư mục PRN / PNG theo thời gian thực (Watchdog)
- 🖨️ Chuyển file **PRN (ESC/POS)** sang **PNG**
- 🔍 OCR tiếng Việt bằng **Tesseract**
- 📤 Gửi ảnh + nội dung hóa đơn lên **Telegram**
- ⚠️ Tự động phát hiện **chênh lệch tiền (VI PHẠM)**
- 🧠 Chống xử lý trùng file (dedup + in-progress lock)
- 🧹 Tự động dọn file sau khi xử lý

---

## 📁 CẤU TRÚC THƯ MỤC

```text
project/
│
├── main.py                  # Entry point – khởi động toàn bộ hệ thống
├── config.py                # Cấu hình chung (BOT TOKEN, PATH, CHAT ID)
├── state.py                 # Bộ nhớ tạm & lock (dedup, concurrency)
│
├── utils/
│   ├── __init__.py
│   └── text_utils.py        # Chuẩn hóa text, parse tiền tệ
│
├── ocr/
│   ├── __init__.py
│   ├── prn_converter.py     # Chuyển PRN → PNG (ESC/POS bitmap)
│   └── ocr_extractor.py     # OCR + trích xuất dữ liệu hóa đơn
│
├── telegram_bot/
│   ├── __init__.py
│   └── sender.py            # Gửi ảnh & tin nhắn Telegram
│
├── processor/
│   ├── __init__.py
│   ├── prn_processor.py     # Xử lý file PRN
│   ├── png_processor.py     # Xử lý file PNG
│   └── violation_checker.py # Kiểm tra & cảnh báo sai phạm
│
├── watcher/
│   ├── __init__.py
│   └── handlers.py          # Watchdog handlers (PRN / PNG)
│
└── worker.py                # Async worker xử lý hàng đợi

```
---

## ⚙️ LUỒNG HOẠT ĐỘNG

1. **Watchdog**
   - Theo dõi thư mục PRN & PNG
   - Khi có file mới → đẩy vào queue

2. **Worker**
   - Nhận file từ queue
   - Phân loại PRN / PNG

3. **PRN Processor**
   - Convert PRN → PNG
   - OCR → parse dữ liệu
   - Gửi Telegram
   - Lưu tạm để so sánh

4. **PNG Processor**
   - OCR trực tiếp
   - Gửi Telegram
   - Lưu tạm để so sánh

5. **Violation Checker**
   - Khi đủ 2 hóa đơn cùng số HĐ:
     - Tạm tính
     - Thanh toán
   - Nếu `Tạm tính > Thanh toán` → CẢNH BÁO

---

## 🧠 QUẢN LÝ TRẠNG THÁI

- `processed_file_set`  
  → File đã xử lý, tránh trùng lặp

- `in_progress_file_set`  
  → File đang xử lý, chống race-condition

- `TEMP_STORAGE`  
  → Lưu dữ liệu hóa đơn theo `Số HĐ`

- `state_lock`  
  → Đảm bảo thread-safe

---

## 📦 YÊU CẦU HỆ THỐNG

- Python 3.9+
- Tesseract OCR (có language `vie`)
- Các thư viện Python:
  ```bash
  pip install pillow pytesseract watchdog python-telegram-bot numpy
# karaoke-invoice-monitoring-system
